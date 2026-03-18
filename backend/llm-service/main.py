import json
import os
import time
from typing import Optional, Tuple

import pika
import requests

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
KEY_MANAGER_URL = os.getenv("KEY_MANAGER_URL", "http://key-manager:8000")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_MODELS = [
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen-vl-plus:free",
    "mistralai/mistral-7b-instruct:free",
]

SCALAR_FIELDS = [
    "CAE",
    "vendor",
    "customer",
    "due_date",
    "vendor_CUIT",
    "vendor_IIBB",
    "CAE_due_date",
    "customer_CUIT",
    "document_type",
    "emission_date",
    "invoice_number",
    "vendor_address",
    "condition_of_IVA",
    "activity_start_date",
]


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


def default_item() -> dict:
    return {
        "code": "",
        "quantity": 0,
        "unit_price": 0,
        "description": "",
        "discount_percentage": 0,
        "unit_price_with_discount": 0,
    }


def default_payload() -> dict:
    return {
        "CAE": "",
        "items": [],
        "vendor": "",
        "customer": "",
        "due_date": "",
        "vendor_CUIT": "",
        "vendor_IIBB": "",
        "CAE_due_date": "",
        "customer_CUIT": "",
        "document_type": "invoice",
        "emission_date": "",
        "invoice_number": "",
        "vendor_address": "",
        "condition_of_IVA": "",
        "activity_start_date": "",
    }


def coerce_number(value):
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "")
        if cleaned == "":
            return 0
        try:
            return int(cleaned)
        except ValueError:
            pass
        try:
            return float(cleaned)
        except ValueError:
            return 0
    return 0


def normalize_item(item: dict) -> dict:
    normalized = default_item()
    if not isinstance(item, dict):
        return normalized

    normalized["code"] = str(item.get("code") or "")
    normalized["quantity"] = coerce_number(item.get("quantity"))
    normalized["unit_price"] = coerce_number(item.get("unit_price"))
    normalized["description"] = str(item.get("description") or "")
    normalized["discount_percentage"] = coerce_number(item.get("discount_percentage"))
    normalized["unit_price_with_discount"] = coerce_number(item.get("unit_price_with_discount"))
    return normalized


def normalize_json_payload(payload: dict) -> dict:
    normalized = default_payload()
    if not isinstance(payload, dict):
        return normalized

    for field in SCALAR_FIELDS:
        normalized[field] = str(payload.get(field) or "")

    normalized["document_type"] = normalized["document_type"] or "invoice"

    items = payload.get("items")
    if isinstance(items, list):
        normalized["items"] = [normalize_item(item) for item in items]

    return normalized


def strip_code_fences(content: str) -> str:
    cleaned = (content or "").strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def extract_balanced_json_object(content: str) -> Optional[str]:
    text = content or ""
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]

    return None


def parse_json_response(content: str) -> Optional[dict]:
    candidates = []
    raw = (content or "").strip()
    if raw:
        candidates.append(raw)

    stripped = strip_code_fences(raw)
    if stripped and stripped not in candidates:
        candidates.append(stripped)

    balanced = extract_balanced_json_object(stripped)
    if balanced and balanced not in candidates:
        candidates.append(balanced)

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    return None


def build_conversion_prompt(text: str) -> str:
    return f"""
Analyze the extracted document text and return ONLY one valid JSON object.
Use exactly this schema and do not add extra keys:
{{
  "CAE": "74237438917416",
  "items": [
    {{
      "code": "300-0030",
      "quantity": 276,
      "unit_price": 1895,
      "description": "DESINFECTANTE SMELL FRESH ORIGINAL X 360ML",
      "discount_percentage": 0,
      "unit_price_with_discount": 523020
    }}
  ],
  "vendor": "TODO CERCA S.A.",
  "customer": "MUNICIPALIDAD PERGAMINO",
  "due_date": "05/07/2024",
  "vendor_CUIT": "30711092567",
  "vendor_IIBB": "0",
  "CAE_due_date": "15/06/2024",
  "customer_CUIT": "30999034515",
  "document_type": "invoice",
  "emission_date": "05/06/2024",
  "invoice_number": "0007-00004983",
  "vendor_address": "Beltrán Nº 498, BUENOS AIRES.PERGAMINO",
  "condition_of_IVA": "EXENTO",
  "activity_start_date": "01/03/2023"
}}
Rules:
- Return ONLY JSON.
- Keep all keys present even if a value is missing.
- If a value is missing, use empty string, 0, or [] as appropriate.
- Do not wrap the JSON in markdown.
- `document_type` must be `invoice` when the document is an invoice.
- `unit_price_with_discount` is the line total after discount.
- Do not invent products not present in the source text.

TEXT:
{text}
""".strip()


def request_openrouter(headers: dict, payload: dict) -> Tuple[Optional[str], Optional[dict]]:
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90)

    if response.status_code == 200:
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        usage = normalize_token_usage(result.get("usage"))
        return content, usage
    if response.status_code == 429:
        raise RuntimeError("rate_limit")
    if response.status_code == 404:
        raise LookupError("model_not_found")
    if response.status_code in [401, 402]:
        raise PermissionError("api_key_error")
    raise RuntimeError(f"unexpected_status_{response.status_code}")


def repair_json_response(text: str, invalid_content: str, headers: dict, model: str) -> Tuple[Optional[dict], Optional[dict]]:
    repair_prompt = f"""
The previous answer was not valid JSON. Rebuild it and return ONLY one valid JSON object.
Use exactly this schema and do not add extra keys:
{{
  "CAE": "",
  "items": [
    {{
      "code": "",
      "quantity": 0,
      "unit_price": 0,
      "description": "",
      "discount_percentage": 0,
      "unit_price_with_discount": 0
    }}
  ],
  "vendor": "",
  "customer": "",
  "due_date": "",
  "vendor_CUIT": "",
  "vendor_IIBB": "",
  "CAE_due_date": "",
  "customer_CUIT": "",
  "document_type": "invoice",
  "emission_date": "",
  "invoice_number": "",
  "vendor_address": "",
  "condition_of_IVA": "",
  "activity_start_date": ""
}}
Use the source text as the authority. The invalid draft may help but can be incomplete.
Return ONLY JSON.

SOURCE TEXT:
{text}

INVALID DRAFT:
{invalid_content}
""".strip()

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": repair_prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "max_tokens": 4096,
    }

    try:
        repaired_content, usage = request_openrouter(headers, payload)
    except Exception as error:
        print(f"Repair pass failed with {model}: {error}")
        return None, None

    if repaired_content is None:
        return None, usage

    return parse_json_response(repaired_content), usage


def convert_to_json(text: str, api_key_data: dict) -> Tuple[Optional[dict], Optional[str], Optional[dict]]:
    api_key = api_key_data["key"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/muniperga/ocr-platform",
        "X-Title": "OCR Platform",
    }

    prompt = build_conversion_prompt(text)

    for model in OPENROUTER_MODELS:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "max_tokens": 4096,
        }

        retry_count = 0
        max_api_retries = 3
        backoff_time = 5
        print(f"Attempting JSON conversion with model: {model}")

        while retry_count < max_api_retries:
            try:
                content, usage = request_openrouter(headers, payload)
                parsed = parse_json_response(content or "")
                if parsed is not None:
                    return normalize_json_payload(parsed), model, usage

                print(f"Primary JSON parsing failed with {model}. Attempting repair pass.")
                repaired, repair_usage = repair_json_response(text, content or "", headers, model)
                total_usage = merge_token_usage(usage, repair_usage)
                if repaired is not None:
                    return normalize_json_payload(repaired), model, total_usage

                print(f"Repair parsing failed with {model}; trying next model.")
                break
            except RuntimeError as error:
                if str(error) == "rate_limit":
                    print(f"Rate limit hit (429) for {model}. Retrying in {backoff_time}s... ({retry_count + 1}/{max_api_retries})")
                    time.sleep(backoff_time)
                    retry_count += 1
                    backoff_time *= 2
                    continue
                print(f"Unexpected runtime error from {model}: {error}")
                break
            except LookupError:
                print(f"Model {model} not found (404), trying next model...")
                break
            except PermissionError:
                print("API Key error while converting JSON")
                report_key_error(api_key_data["id"])
                return None, None, None
            except Exception as e:
                print(f"Exception with model {model}: {e}")
                retry_count += 1
                time.sleep(1)

        print(f"Model {model} failed, moving to next model in list...")

    report_key_error(api_key_data["id"])
    return None, None, None


def callback(ch, method, properties, body):
    data = json.loads(body)
    doc_id = data.get("document_id")
    raw_text = data.get("raw_text")
    ocr_model_used = data.get("ocr_model_used")
    ocr_token_usage = data.get("ocr_token_usage")

    print(f"Converting text to JSON for document {doc_id}")
    success = False

    try:
        keys_response = requests.get(f"{KEY_MANAGER_URL}/keys/active", timeout=5)
        active_keys = keys_response.json() if keys_response.status_code == 200 else []
    except Exception:
        active_keys = []

    if not active_keys:
        print("No active API keys found in database.")

    for api_key_data in active_keys:
        print(f"Trying API Key ID: {api_key_data['id']} for JSON conversion")
        json_data, llm_model_used, llm_token_usage = convert_to_json(raw_text, api_key_data)
        if json_data is not None:
            message = json.dumps(
                {
                    "document_id": doc_id,
                    "json_result": json_data,
                    "llm_model_used": llm_model_used,
                    "llm_token_usage": llm_token_usage,
                    "ocr_model_used": ocr_model_used,
                    "ocr_token_usage": ocr_token_usage,
                }
            )
            ch.basic_publish(
                exchange="",
                routing_key="processing_complete",
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
            )
            print(f"JSON conversion complete for {doc_id}")
            success = True
            break
        print(f"Key {api_key_data['id']} failed for JSON, trying next...")
        time.sleep(1)

    if not success:
        print(f"Failed to process JSON for {doc_id}")
        error_msg = "JSON conversion failed after trying all API keys."
        fail_message = json.dumps(
            {
                "document_id": doc_id,
                "error": error_msg,
                "ocr_model_used": ocr_model_used,
                "ocr_token_usage": ocr_token_usage,
            }
        )
        ch.basic_publish(
            exchange="",
            routing_key="processing_failed",
            body=fail_message,
            properties=pika.BasicProperties(delivery_mode=2),
        )

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
    channel.queue_declare(queue="text_extracted", durable=True)
    channel.queue_declare(queue="processing_complete", durable=True)
    channel.queue_declare(queue="processing_failed", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="text_extracted", on_message_callback=callback)

    print(f"LLM Service ({OPENROUTER_MODELS[0]}) is waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
