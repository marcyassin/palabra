-- migrate:up
CREATE TABLE book_words (
    book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    word_id INT NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    count INT NOT NULL DEFAULT 1,
    PRIMARY KEY (book_id, word_id)
);

-- migrate:down
DROP TABLE IF EXISTS book_words;

