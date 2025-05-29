package model

import (
	"encoding/json"
	"errors"
)

type User struct {
	BaseEntity
	IPerson
	Id           string `json:"id" db:"id"`
	Meta         *json.RawMessage `json:"meta" db:"meta"`
}

type GetUserFilters struct {
	Id           *string `json:"id" db:"id"`
	Email        *string `json:"email" db:"email"`
	Phone        *string `json:"phone" db:"phone"`
	AuthProvider *string `json:"auth_provider" db:"auth_provider"`
	IsActive     *bool   `json:"is_active" db:"is_active"`
}

func ValidateUser(user *User) error {
	if user.Name == "" {
		return errors.New("name is required")
	}
	if user.Email == "" && user.Phone == "" {
		return errors.New("either email or phone is required")
	}
	if user.AuthProvider == "" {
		return errors.New("auth provider is required")
	}
	return nil
}
