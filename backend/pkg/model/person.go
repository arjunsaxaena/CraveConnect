package model

type IPerson struct {
	Id           string `json:"id" db:"id"`
	Name         string `json:"name" db:"name"`
	Email        string `json:"email" db:"email"`
	Phone        string `json:"phone" db:"phone"`
	AuthProvider string `json:"auth_provider" db:"auth_provider"`
}
