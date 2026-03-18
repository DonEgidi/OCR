import base64
import json
import os
import time
from typing import Dict, List, Optional, Tuple

import pika
import requests

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
KEY_MANAGER_URL = os.getenv("KEY_MANAGER_URL", "http://key-manager:8000")
FTP_API_URL = os.getenv("FTP_API_URL", "http://ftp-api:8007")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

OCR_MODELS = [
    "nvidia/nemotron-nano-12b-2-vl:free",
    "nvidia/llama-nemotron-embed-vl-1b-v2:free",
    "openrouter/healer-alpha",
    "openrouter/hunter-alpha",
    "google/gemini-2.0-flash-lite-001:free",
]

IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def normalize_token_usage(usage: Optional[dict]) -> Optional[dict]:
    if not isinstance(usage, dict):
        return None
    return {
        "prompt_tokens": int(usage.get("prompt_tokens") or 0),
        "completion_tokens": int(usage.get("completion_tokens") or 0),
        "total_tokens": int(usage.get("total_tokens") or 0),
    }


def merge_token_usage(current: Optional[dict], incoming: Optional[dict]) -> Optional[dict]:
    if current is None and incoming is None:
        return None

    merged = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }

    for source in [current, incoming]:
        normalized = normalize_token_usage(source)
        if normalized is None:
            continue
        merged["prompt_tokens"] += normalized["prompt_tokens"]
        merged["completion_tokens"] += normalized["completion_tokens"]
        merged["total_tokens"] += normalized["total_tokens"]

    return merged


def report_key_error(key_id):
    try:
        requests.post(f"{KEY_MANAGER_URL}/keys/report-error/{key_id}", timeout=5)
    except Exception as e:
        print(f"Error reporting key error: {e}")


def extract_text_from_pdf(pdf_content: bytes) -> str:
    import fitz

    text = ""
    try:
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def render_pdf_to_images(pdf_content: bytes) -> List[bytes]:
    import fitz

    images = []
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        for page in doc:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            images.append(pixmap.tobytes("png"))
    return images


def perform_ocr(
    image_bytes: bytes,
    api_key_data: dict,
    mime_type: str = "image/jpeg",
) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
    api_key = api_key_data["key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/muniperga/ocr-platform",
        "X-Title": "OCR Platform",
    }

    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{base64_image}"
    prompt = "Extract all text from the provided image accurately. Do not add any summary or explanation."

    for model in OCR_MODELS:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
        }

        retry_count = 0
        max_api_retries = 3
        backoff_time = 5
        print(f"Attempting OCR with model: {model}")

        while retry_count < max_api_retries:
            try:
                response = requests.post(
                    OPENROUTER_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90,
                )
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    token_usage = normalize_token_usage(result.get("usage"))
                    return content, model, token_usage
                if response.status_code == 429:
                    print(f"Rate limit hit (429) for {model}. Retrying in {backoff_time}s... ({retry_count + 1}/{max_api_retries})")
                    time.sleep(backoff_time)
                    retry_count += 1
                    backoff_time *= 2
                    continue
                if response.status_code == 404:
                    print(f"Model {model} not found (404), trying next model...")
                    break
                if response.status_code in [401, 402]:
                    print(f"API Key error: {response.status_code}")
                    report_key_error(api_key_data["id"])
                    return None, None, None
                print(f"Unexpected API response for {model}: {response.status_code} - {response.text}")
                break
            except Exception as e:
                print(f"Exception during OCR with {model}: {e}")
                retry_count += 1
                time.sleep(backoff_time)
                backoff_time *= 1.5

        print(f"Model {model} failed or rate-limited, moving to next model...")

    report_key_error(api_key_data["id"])
    return None, None, None


def get_active_keys() -> List[dict]:
    try:
        keys_response = requests.get(f"{KEY_MANAGER_URL}/keys/active", timeout=5)
        if keys_response.status_code == 200:
            return keys_response.json()
    except Exception as e:
        print(f"Error loading active API keys: {e}")
    return []


def publish_json(channel, routing_key: str, payload: dict):
    channel.queue_declare(queue=routing_key, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=routing_key,
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )


def fail_document(
    channel,
    doc_id: str,
    error: str,
    ocr_model_used: Optional[str] = None,
    ocr_token_usage: Optional[dict] = None,
):
    payload = {"document_id": doc_id, "error": error}
    if ocr_model_used:
        payload["ocr_model_used"] = ocr_model_used
    if ocr_token_usage:
        payload["ocr_token_usage"] = ocr_token_usage
    publish_json(channel, "processing_failed", payload)


def ocr_pdf_pages(pdf_content: bytes, active_keys: List[dict]) -> Tuple[Optional[str], Optional[str], Optional[dict]]:
    rendered_pages = render_pdf_to_images(pdf_content)
    page_texts = []
    models_used = []
    total_token_usage = None

    for page_number, image_bytes in enumerate(rendered_pages, start=1):
        page_text = None
        page_model = None
        page_token_usage = None
        for api_key_data in active_keys:
            print(f"Trying API Key ID: {api_key_data['id']} for PDF page {page_number}")
            page_text, page_model, page_token_usage = perform_ocr(image_bytes, api_key_data, "image/png")
            if page_text:
                break
            time.sleep(1)

        if not page_text:
            print(f"Failed OCR for PDF page {page_number}")
            return None, ", ".join(dict.fromkeys(models_used)) if models_used else None, total_token_usage

        if page_model:
            models_used.append(page_model)
        total_token_usage = merge_token_usage(total_token_usage, page_token_usage)
        page_texts.append(page_text.strip())

    model_summary = ", ".join(dict.fromkeys(models_used)) if models_used else None
    return "\n\n".join(text for text in page_texts if text), model_summary, total_token_usage


def callback(ch, method, properties, body):
    data = json.loads(body)
    doc_id = data.get("document_id")
    ftp_path = data.get("ftp_path")

    print(f"Processing OCR for document {doc_id} at {ftp_path}")

    download_url = f"{FTP_API_URL}/files/download?file_path={ftp_path}"
    ext = os.path.splitext(ftp_path)[1].lower()
    is_pdf = ext == ".pdf"
    mime_type = IMAGE_MIME_TYPES.get(ext, "image/jpeg")
    text = None
    file_content = None
    ocr_model_used = None
    ocr_token_usage = None

    try:
        resp = requests.get(download_url, timeout=30)
        if resp.status_code == 200:
            file_content = resp.content
        else:
            error = f"Failed to download {ftp_path} from FTP API: {resp.status_code}"
            print(error)
            fail_document(ch, doc_id, error)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
    except Exception as e:
        error = f"Error downloading file {doc_id}: {e}"
        print(error)
        fail_document(ch, doc_id, error)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    if is_pdf:
        print(f"Detected PDF for {doc_id}. Attempting direct extraction...")
        text = extract_text_from_pdf(file_content)
        if text and text.strip():
            ocr_model_used = "pymupdf_text_extraction"
            ocr_token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            print(f"Successfully extracted text from PDF {doc_id}")
        else:
            print(f"PDF {doc_id} appears to be scanned. Falling back to rendered page OCR.")
            active_keys = get_active_keys()
            if not active_keys:
                fail_document(ch, doc_id, "No active API keys found for OCR processing.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            text, ocr_model_used, ocr_token_usage = ocr_pdf_pages(file_content, active_keys)
    else:
        active_keys = get_active_keys()
        if not active_keys:
            fail_document(ch, doc_id, "No active API keys found for OCR processing.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        for api_key_data in active_keys:
            print(f"Trying API Key ID: {api_key_data['id']}")
            text, ocr_model_used, ocr_token_usage = perform_ocr(file_content, api_key_data, mime_type)
            if text:
                break
            print(f"Key {api_key_data['id']} failed, trying next...")
            time.sleep(1)

    if text and text.strip():
        message = {
            "document_id": doc_id,
            "raw_text": text,
            "ftp_path": ftp_path,
            "ocr_model_used": ocr_model_used,
            "ocr_token_usage": ocr_token_usage,
        }
        publish_json(ch, "text_extracted", message)
        publish_json(ch, "ocr_complete", message)
        print(f"Processing complete for {doc_id}")
    else:
        print(f"Failed to process {doc_id}")
        fail_document(ch, doc_id, "OCR extraction failed after trying all API keys.", ocr_model_used, ocr_token_usage)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    max_retries = 10
    connection = None
    for i in range(max_retries):
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            print("Connected to RabbitMQ")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ not ready, retrying in 5s... ({i + 1}/{max_retries})")
            time.sleep(5)

    if not connection:
        print("Could not connect to RabbitMQ, exiting.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="document_uploaded", durable=True)
    channel.queue_declare(queue="text_extracted", durable=True)
    channel.queue_declare(queue="ocr_complete", durable=True)
    channel.queue_declare(queue="processing_failed", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="document_uploaded", on_message_callback=callback)

    print("OCR Service is waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
