---Schema for neon postgres instance
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID,
    chunk_index INTEGER,
    title TEXT,
    company_name TEXT,
    source_name TEXT,
    url TEXT,
    chunk_text TEXT,
    vector vector(1536),
    published_at DATE
);