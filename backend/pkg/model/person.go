package model

const (
	AuthProviderGoogle = "google"
	AuthProviderPhone  = "phone"
)

type IPerson struct {
	Name         string `json:"name" db:"name"`
	Email        string `json:"email" db:"email"`
	Phone        string `json:"phone" db:"phone"`
	AuthProvider string `json:"auth_provider" db:"auth_provider"`
}
