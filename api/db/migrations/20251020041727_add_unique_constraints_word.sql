-- migrate:up
ALTER TABLE words
ADD CONSTRAINT unique_word_language UNIQUE (word, language);

-- migrate:down
ALTER TABLE words
DROP CONSTRAINT IF EXISTS unique_word_language;

