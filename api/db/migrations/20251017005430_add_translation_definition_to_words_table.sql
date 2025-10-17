-- migrate:up

ALTER TABLE public.words
    DROP COLUMN IF EXISTS frequency;

ALTER TABLE public.words
    ADD COLUMN translation text,
    ADD COLUMN definition_en text,
    ADD COLUMN definition_local text;


-- migrate:down

ALTER TABLE public.words
    DROP COLUMN IF EXISTS translation,
    DROP COLUMN IF EXISTS definition_en,
    DROP COLUMN IF EXISTS definition_local;

ALTER TABLE public.words
    ADD COLUMN frequency integer DEFAULT 0;

