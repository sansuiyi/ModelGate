CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(255) PRIMARY KEY,
    data TEXT NOT NULL,
    created_at VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS request_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    timestamp VARCHAR(100) NOT NULL,
    prompt_preview TEXT,
    classification VARCHAR(50),
    selected_provider VARCHAR(100),
    selected_model VARCHAR(100),
    reason TEXT,
    latency_ms INT,
    estimated_cost DOUBLE,
    tokens_used INT DEFAULT 0,
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    ttft_ms INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'success',
    candidates_considered TEXT DEFAULT '[]',
    candidates_eliminated TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS global_models (
    model_name VARCHAR(255) PRIMARY KEY,
    enabled INT DEFAULT 1,
    description TEXT DEFAULT '',
    custom_config TEXT DEFAULT '{}'
);
