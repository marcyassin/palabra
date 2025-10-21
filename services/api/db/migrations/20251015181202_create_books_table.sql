-- migrate:up
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT,
    language TEXT NOT NULL,
    user_id INT,
    status TEXT NOT NULL DEFAULT 'pending',
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    processed TIMESTAMP
);

-- migrate:down
DROP TABLE IF EXISTS books;
