from datetime import datetime
import asyncio
import json
import os
import threading
import time
import uuid

import pika
import requests
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import Column, DateTime, String, select, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI(title="OCR Platform API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/ocr_db")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
FTP_API_URL = os.getenv("FTP_API_URL", "http://ftp-api:8007")
KEY_MANAGER_URL = os.getenv("KEY_MANAGER_URL", "http://key-manager:8000")

engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    ftp_path = Column(String, nullable=False)
    status = Column(String, default="pending")
    raw_text = Column(String)
    json_result = Column(JSONB)
    error_message = Column(String)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    ocr_model_used = Column(String)
    llm_model_used = Column(String)
    ocr_token_usage = Column(JSONB)
    llm_token_usage = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def serialize_datetime(value):
    return value.isoformat() if value else None


def serialize_document(doc: Document) -> dict:
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "ftp_path": doc.ftp_path,
        "status": doc.status,
        "raw_text": doc.raw_text,
        "json_result": doc.json_result,
        "error_message": doc.error_message,
        "processing_started_at": serialize_datetime(doc.processing_started_at),
        "processing_completed_at": serialize_datetime(doc.processing_completed_at),
        "ocr_model_used": doc.ocr_model_used,
        "llm_model_used": doc.llm_model_used,
        "ocr_token_usage": doc.ocr_token_usage,
        "llm_token_usage": doc.llm_token_usage,
        "created_at": serialize_datetime(doc.created_at),
        "updated_at": serialize_datetime(doc.updated_at),
    }


async def ensure_document_columns():
    statements = [
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP WITHOUT TIME ZONE",
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS processing_completed_at TIMESTAMP WITHOUT TIME ZONE",
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS ocr_model_used TEXT",
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS llm_model_used TEXT",
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS ocr_token_usage JSONB",
        "ALTER TABLE documents ADD COLUMN IF NOT EXISTS llm_token_usage JSONB",
    ]
    async with engine.begin() as conn:
        for statement in statements:
            await conn.execute(text(statement))


async def log_processing_event(document_id: uuid.UUID, service_name: str, message: str, level: str = "info"):
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                text(
                    """
                    INSERT INTO processing_logs (document_id, service_name, message, level)
                    VALUES (:document_id, :service_name, :message, :level)
                    """
                ),
                {
                    "document_id": document_id,
                    "service_name": service_name,
                    "message": message,
                    "level": level,
                },
            )
            await session.commit()
    except Exception as exc:
        print(f"Processing log insert failed for {document_id}: {exc}")


def publish_message(routing_key: str, message: dict) -> bool:
    max_retries = 5
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue=routing_key, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Error publishing message (attempt {i + 1}/{max_retries}): {e}")
            time.sleep(2)
    return False


def build_storage_path(doc_id: uuid.UUID, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    safe_name = os.path.basename(filename).replace(" ", "_")
    return f"/{doc_id}_{safe_name}{'' if safe_name.lower().endswith(ext) else ext}"


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    doc_id = uuid.uuid4()
    started_at = datetime.utcnow()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".pdf"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    ftp_path = build_storage_path(doc_id, file.filename)

    try:
        files = {"file": (file.filename, file.file, file.content_type)}
        params = {"destination_path": ftp_path}
        ftp_response = requests.post(
            f"{FTP_API_URL}/files/upload",
            files=files,
            params=params,
            timeout=30,
        )
        if ftp_response.status_code != 200:
            detail = ftp_response.text
            try:
                detail = ftp_response.json().get("detail", detail)
            except Exception:
                pass
            raise HTTPException(status_code=500, detail=f"FTP API Error ({ftp_response.status_code}): {detail}")

        ftp_data = ftp_response.json()
        ftp_path = ftp_data.get("destination_path") or ftp_data.get("path") or ftp_path
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Detailed FTP Error: {e}")
        raise HTTPException(status_code=500, detail=f"Gateway FTP Error: {str(e)}")

    async with AsyncSessionLocal() as session:
        new_doc = Document(
            id=doc_id,
            filename=file.filename,
            ftp_path=ftp_path,
            status="extracting",
            processing_started_at=started_at,
            processing_completed_at=None,
            ocr_model_used=None,
            llm_model_used=None,
            ocr_token_usage=None,
            llm_token_usage=None,
        )
        session.add(new_doc)
        await session.commit()

    await log_processing_event(doc_id, "api-gateway", f"Document uploaded to FTP path {ftp_path}")

    message = {"document_id": str(doc_id), "ftp_path": ftp_path}
    published = publish_message("document_uploaded", message)
    if not published:
        async with AsyncSessionLocal() as session:
            doc = await session.get(Document, doc_id)
            if doc:
                doc.status = "failed"
                doc.error_message = "Could not enqueue document for OCR processing."
                doc.processing_completed_at = datetime.utcnow()
                await session.commit()
        await log_processing_event(doc_id, "api-gateway", "Failed to enqueue document for OCR processing", "error")
        raise HTTPException(status_code=500, detail="Document uploaded but could not be enqueued for processing")

    await log_processing_event(doc_id, "api-gateway", "Document enqueued for OCR processing")
    return {"document_id": str(doc_id), "status": "extracting"}


@app.get("/documents")
async def list_documents():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Document).order_by(Document.created_at.desc()))
        docs = result.scalars().all()
        return [serialize_document(doc) for doc in docs]


@app.get("/documents/{doc_id}")
async def get_document(doc_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return serialize_document(doc)


@app.post("/documents/{doc_id}/reprocess")
async def reprocess_document(doc_id: str):
    async with AsyncSessionLocal() as session:
        doc_uuid = uuid.UUID(doc_id)
        doc = await session.get(Document, doc_uuid)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        doc.status = "extracting"
        doc.raw_text = None
        doc.json_result = None
        doc.error_message = None
        doc.processing_started_at = datetime.utcnow()
        doc.processing_completed_at = None
        doc.ocr_model_used = None
        doc.llm_model_used = None
        doc.ocr_token_usage = None
        doc.llm_token_usage = None
        await session.commit()

        ftp_path = doc.ftp_path

    published = publish_message("document_uploaded", {"document_id": doc_id, "ftp_path": ftp_path})
    if not published:
        async with AsyncSessionLocal() as session:
            retry_doc = await session.get(Document, doc_uuid)
            if retry_doc:
                retry_doc.status = "failed"
                retry_doc.error_message = "Could not enqueue document for reprocessing."
                retry_doc.processing_completed_at = datetime.utcnow()
                await session.commit()
        await log_processing_event(doc_uuid, "api-gateway", "Failed to enqueue document for reprocessing", "error")
        raise HTTPException(status_code=500, detail="Could not enqueue document for reprocessing")

    await log_processing_event(doc_uuid, "api-gateway", "Document reprocessing requested")
    return {"message": "Reprocessing started", "document_id": doc_id}


@app.get("/documents/{doc_id}/original")
async def view_document_original(doc_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        ftp_path = doc.ftp_path
        filename = doc.filename

    try:
        ftp_response = requests.get(
            f"{FTP_API_URL}/files/view",
            params={"file_path": ftp_path},
            timeout=60,
        )
        if ftp_response.status_code != 200:
            detail = ftp_response.text
            try:
                detail = ftp_response.json().get("detail", detail)
            except Exception:
                pass
            raise HTTPException(status_code=ftp_response.status_code, detail=f"FTP API Error: {detail}")

        media_type = ftp_response.headers.get("content-type", "application/octet-stream")
        response_headers = {
            "Content-Disposition": f"inline; filename=\"{os.path.basename(filename)}\""
        }
        content_length = ftp_response.headers.get("content-length")
        if content_length:
            response_headers["Content-Length"] = content_length
        return Response(content=ftp_response.content, media_type=media_type, headers=response_headers)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway FTP View Error: {e}")


@app.get("/keys")
async def proxy_list_keys():
    try:
        resp = requests.get(f"{KEY_MANAGER_URL}/keys", timeout=10)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key Manager Error: {e}")


@app.post("/keys")
async def proxy_add_key(data: dict):
    try:
        resp = requests.post(f"{KEY_MANAGER_URL}/keys", json=data, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.json().get("detail", "Error"))
        return resp.json()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key Manager Error: {e}")


@app.post("/keys/report-error/{key_id}")
async def proxy_report_error(key_id: int):
    try:
        resp = requests.post(f"{KEY_MANAGER_URL}/keys/report-error/{key_id}", timeout=10)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key Manager Error: {e}")


@app.post("/keys/reactivate/{key_id}")
async def proxy_reactivate_key(key_id: int):
    try:
        resp = requests.post(f"{KEY_MANAGER_URL}/keys/reactivate/{key_id}", timeout=10)
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key Manager Error: {e}")


def consume_results():
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.queue_declare(queue="processing_complete", durable=True)
            channel.queue_declare(queue="ocr_complete", durable=True)
            channel.queue_declare(queue="processing_failed", durable=True)

            def callback(ch, method, properties, body):
                data = json.loads(body)
                doc_id = data.get("document_id")

                async def update_doc() -> bool:
                    print(f"Update background worker: received {method.routing_key} for {doc_id}")
                    async with AsyncSessionLocal() as session:
                        try:
                            doc_uuid = uuid.UUID(doc_id)
                            doc = await session.get(Document, doc_uuid)
                            if not doc:
                                print(f"Document {doc_id} not found in database")
                                return True

                            if method.routing_key == "ocr_complete":
                                doc.raw_text = data.get("raw_text")
                                doc.status = "converting"
                                doc.ocr_model_used = data.get("ocr_model_used")
                                doc.ocr_token_usage = data.get("ocr_token_usage")
                                await session.commit()
                                await log_processing_event(doc_uuid, "ocr-service", f"OCR completed using {doc.ocr_model_used or 'unknown model'}")
                            elif method.routing_key == "processing_complete":
                                doc.json_result = data.get("json_result")
                                doc.status = "completed"
                                doc.llm_model_used = data.get("llm_model_used")
                                doc.llm_token_usage = data.get("llm_token_usage")
                                if data.get("ocr_model_used"):
                                    doc.ocr_model_used = data.get("ocr_model_used")
                                if data.get("ocr_token_usage") is not None:
                                    doc.ocr_token_usage = data.get("ocr_token_usage")
                                doc.processing_completed_at = datetime.utcnow()
                                await session.commit()
                                await log_processing_event(doc_uuid, "llm-service", f"JSON conversion completed using {doc.llm_model_used or 'unknown model'}")
                            elif method.routing_key == "processing_failed":
                                doc.status = "failed"
                                doc.error_message = data.get("error")
                                doc.processing_completed_at = datetime.utcnow()
                                if data.get("ocr_model_used"):
                                    doc.ocr_model_used = data.get("ocr_model_used")
                                if data.get("llm_model_used"):
                                    doc.llm_model_used = data.get("llm_model_used")
                                if data.get("ocr_token_usage") is not None:
                                    doc.ocr_token_usage = data.get("ocr_token_usage")
                                if data.get("llm_token_usage") is not None:
                                    doc.llm_token_usage = data.get("llm_token_usage")
                                await session.commit()
                                await log_processing_event(doc_uuid, "pipeline", data.get("error", "Processing failed"), "error")
                            return True
                        except Exception as inner_e:
                            print(f"Error in update_doc coroutine: {inner_e}")
                            await session.rollback()
                            return False

                fut = asyncio.run_coroutine_threadsafe(update_doc(), app.state.loop)
                try:
                    updated = fut.result(timeout=10)
                    if updated:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except asyncio.TimeoutError:
                    print(f"Timeout updating document {doc_id} in background thread")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except Exception as e:
                    print(f"Error waiting for update_doc for {doc_id}: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            channel.basic_consume(queue="processing_complete", on_message_callback=callback)
            channel.basic_consume(queue="ocr_complete", on_message_callback=callback)
            channel.basic_consume(queue="processing_failed", on_message_callback=callback)

            print("API Gateway result consumer started in separate thread...")
            channel.start_consuming()
        except Exception as e:
            print(f"Consumer error: {e}, restarting in 5s...")
            time.sleep(5)


@app.on_event("startup")
async def startup_event():
    await ensure_document_columns()
    app.state.loop = asyncio.get_running_loop()
    thread = threading.Thread(target=consume_results, daemon=True)
    thread.start()
