package postgres

import (
    "database/sql"

    "marcyassin/palabra/internal/models"
)

type WordModel struct {
    DB *sql.DB
}

func (m *WordModel) Insert(word, language string, difficulty int, translation, definitionEN, definitionLocal string) (int, error) {
    query := `
        INSERT INTO words (word, language, difficulty, translation, definition_en, definition_local, created)
        VALUES ($1, $2, $3, $4, $5, $6, NOW())
        RETURNING id`

    var id int
    err := m.DB.QueryRow(query, word, language, difficulty, translation, definitionEN, definitionLocal).Scan(&id)
    if err != nil {
        return 0, err
    }
    return id, nil
}

func (m *WordModel) Get(id int) (*models.Word, error) {
    query := `
        SELECT id, word, language, difficulty, translation, definition_en, definition_local, created
        FROM words
        WHERE id = $1`

    w := &models.Word{}
    err := m.DB.QueryRow(query, id).Scan(
        &w.ID, &w.Word, &w.Language, &w.Difficulty, &w.Translation, &w.DefinitionEN, &w.DefinitionLocal, &w.Created,
    )
    if err != nil {
        if err == sql.ErrNoRows {
            return nil, models.ErrNoRecord
        }
        return nil, err
    }
    return w, nil
}
