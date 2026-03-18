from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, Boolean, DateTime, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os
from pydantic import BaseModel

app = FastAPI(title="Key Manager Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/ocr_db")
engine = create_async_engine(DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    key_value = Column(String, unique=True, nullable=False)
    provider = Column(String, default="openrouter")
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class APIKeySchema(BaseModel):
    key_value: str
    provider: str = "openrouter"


def serialize_key_public(api_key: APIKey) -> dict:
    key_value = api_key.key_value or ""
    prefix = key_value[:8]
    suffix = key_value[-4:] if len(key_value) >= 4 else key_value
    masked_key = f"{prefix}...{suffix}" if key_value else ""
    return {
        "id": api_key.id,
        "provider": api_key.provider,
        "is_active": api_key.is_active,
        "last_used": api_key.last_used,
        "error_count": api_key.error_count,
        "created_at": api_key.created_at,
        "masked_key": masked_key,
    }


@app.get("/keys/next")
async def get_next_key():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(APIKey).where(APIKey.is_active == True).order_by(APIKey.last_used.asc().nulls_first())
        )
        api_key = result.scalars().first()
        if not api_key:
            raise HTTPException(status_code=404, detail="No active API keys found")

        api_key.last_used = datetime.utcnow()
        await session.commit()
        return {"id": api_key.id, "key": api_key.key_value}


@app.get("/keys/active")
async def get_active_keys():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(APIKey).where(APIKey.is_active == True).order_by(APIKey.last_used.asc().nulls_first())
        )
        keys = result.scalars().all()
        return [{"id": k.id, "key": k.key_value} for k in keys]


@app.post("/keys/report-error/{key_id}")
async def report_error(key_id: int):
    async with AsyncSessionLocal() as session:
        api_key = await session.get(APIKey, key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="Key not found")

        api_key.error_count += 1
        if api_key.error_count >= 5:
            api_key.is_active = False

        await session.commit()
        return {"message": f"Key {key_id} reported and {'deactivated' if not api_key.is_active else 'updated'}"}


@app.post("/keys/reactivate/{key_id}")
async def reactivate_key(key_id: int):
    async with AsyncSessionLocal() as session:
        api_key = await session.get(APIKey, key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="Key not found")
        api_key.is_active = True
        api_key.error_count = 0
        await session.commit()
        return {"message": f"Key {key_id} reactivated"}


@app.post("/keys")
async def add_key(data: APIKeySchema):
    async with AsyncSessionLocal() as session:
        new_key = APIKey(key_value=data.key_value, provider=data.provider)
        session.add(new_key)
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Key already exists or invalid")
        return {"message": "Key added successfully", "id": new_key.id}


@app.get("/keys")
async def list_keys():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(APIKey))
        keys = result.scalars().all()
        return [serialize_key_public(key) for key in keys]
