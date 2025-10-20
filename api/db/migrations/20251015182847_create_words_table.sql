-- migrate:up
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word TEXT NOT NULL,
    language TEXT NOT NULL,
    difficulty INT,
    zipf_score DOUBLE PRECISION DEFAULT 0,
    created TIMESTAMP NOT NULL DEFAULT NOW()
);

-- migrate:down
DROP TABLE IF EXISTS words;
