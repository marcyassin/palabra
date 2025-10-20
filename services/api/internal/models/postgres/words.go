package postgres

import (
    "database/sql"

    "marcyassin/palabra/internal/models"
)

type WordModel struct {
    DB *sql.DB
}

func (m *WordModel) Insert(word string, language string, difficulty int, zipfScore float64) (int, error) {
    query := `
        INSERT INTO words (word, language, difficulty, zipf_score, created)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (word, language)
        DO UPDATE SET
            difficulty = EXCLUDED.difficulty,
            zipf_score = EXCLUDED.zipf_score
        RETURNING id;
    `
    var id int
    err := m.DB.QueryRow(query, word, language, difficulty, zipfScore).Scan(&id)
    if err != nil {
        return 0, err
    }
    return id, nil
}

func (m *WordModel) Get(id int) (*models.Word, error) {
    query := `
        SELECT id, word, language, difficulty, zipf_score, created
        FROM words
        WHERE id = $1;
    `
    w := &models.Word{}
    err := m.DB.QueryRow(query, id).Scan(
        &w.ID, &w.Word, &w.Language, &w.Difficulty, &w.ZipfScore, &w.Created,
    )
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, models.ErrNoRecord
        }
        return nil, err
    }
    return w, nil
}
