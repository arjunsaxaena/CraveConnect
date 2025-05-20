package model

import "errors"

type Restaurant struct {
	BaseEntity
	IPerson
	ImagePath    string `json:"image_path" db:"image_path"`
	MenuPath     string `json:"menu_path" db:"menu_path"`
}

type GetRestaurantFilters struct {
	Id *string `json:"id" db:"id"`
	Name *string `json:"name" db:"name"`
	Email *string `json:"email" db:"email"`
	Phone *string `json:"phone" db:"phone"`
	AuthProvider *string `json:"auth_provider" db:"auth_provider"`
	IsActive *bool `json:"is_active" db:"is_active"`
}

func ValidateRestaurant(restaurant *Restaurant) error {
	
	if restaurant.Name == "" {
		return errors.New("name is required")
	}
	if restaurant.Email == "" {
		return errors.New("email is required")
	}
	if restaurant.Phone == "" {
		return errors.New("phone is required")
	}
	if restaurant.AuthProvider == "" {
		return errors.New("auth provider is required")
	}
	
	return nil
}
