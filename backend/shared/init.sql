-- OCR Platform Database Schema

-- Table for API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key_value TEXT UNIQUE NOT NULL,
    provider TEXT DEFAULT 'openrouter',
    is_active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITHOUT TIME ZONE,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for Documents/Extractions
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    ftp_path TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, extracting, converting, completed, failed
    raw_text TEXT,
    json_result JSONB,
    error_message TEXT,
    processing_started_at TIMESTAMP WITHOUT TIME ZONE,
    processing_completed_at TIMESTAMP WITHOUT TIME ZONE,
    ocr_model_used TEXT,
    llm_model_used TEXT,
    ocr_token_usage JSONB,
    llm_token_usage JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for processing logs
CREATE TABLE IF NOT EXISTS processing_logs (
    id SERIAL PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    service_name TEXT NOT NULL,
    message TEXT NOT NULL,
    level TEXT DEFAULT 'info',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);
