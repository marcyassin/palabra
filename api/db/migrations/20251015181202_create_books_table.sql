-- db/migrations/20251015181202_create_books_table.sql

-- migrate:up
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    language TEXT NOT NULL,
    user_id INT,
    status TEXT NOT NULL DEFAULT 'pending',
    created TIMESTAMP NOT NULL DEFAULT NOW(),
    processed TIMESTAMP
);

-- migrate:down
DROP TABLE IF EXISTS books;
