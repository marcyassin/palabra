-- migrate:up
ALTER TABLE words
ADD CONSTRAINT words_word_language_unique UNIQUE(word, language);

-- migrate:down
ALTER TABLE words
DROP CONSTRAINT IF EXISTS words_word_language_unique;
