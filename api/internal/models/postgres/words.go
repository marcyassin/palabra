package postgres

import (
    "database/sql"

    "marcyassin/bookprep/internal/models"
)

type WordModel struct {
    DB *sql.DB
}

func (m *WordModel) Insert(word, language string, difficulty, frequency int) (int, error) {
    query := `
        INSERT INTO words (word, language, difficulty, frequency, created)
        VALUES ($1, $2, $3, $4, NOW())
        RETURNING id`

    var id int
    err := m.DB.QueryRow(query, word, language, difficulty, frequency).Scan(&id)
    if err != nil {
        return 0, err
    }
    return id, nil
}

func (m *WordModel) Get(id int) (*models.Word, error) {
    query := `
        SELECT id, word, language, difficulty, frequency, created
        FROM words
        WHERE id = $1`

    w := &models.Word{}
    err := m.DB.QueryRow(query, id).Scan(
        &w.ID, &w.Word, &w.Language, &w.Difficulty, &w.Frequency, &w.Created,
    )
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, models.ErrNoRecord
        }
        return nil, err
    }
    return w, nil
}
