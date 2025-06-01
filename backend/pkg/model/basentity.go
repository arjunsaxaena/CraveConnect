package model

import (
	"encoding/json"
	"time"
)

type BaseEntity struct {
	Meta         *json.RawMessage `json:"meta" db:"meta"`
	IsActive  bool            `json:"is_active" db:"is_active"`
	CreatedAt time.Time       `json:"created_at" db:"created_at"`
	UpdatedAt time.Time       `json:"updated_at" db:"updated_at"`
}
