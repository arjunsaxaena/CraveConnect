package model

type IPerson struct {
	Id    string `json:"id" db:"id" form:"id"`
	Name  string `json:"name" db:"name" form:"name"`
	Email string `json:"email" db:"email" form:"email"`
	Phone string `json:"phone" db:"phone" form:"phone"`
	AuthProvider string `json:"auth_provider" db:"auth_provider" form:"auth_provider"`
} 