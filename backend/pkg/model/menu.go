package model

import "errors"

type MenuItem struct {
	BaseEntity
	RestaurantId string  `json:"restaurant_id" db:"restaurant_id"`
	Name         string  `json:"name" db:"name"`
	Description  string  `json:"description" db:"description"`
	Price        float64 `json:"price" db:"price"`
	ImagePath    string  `json:"image_path" db:"image_path"`
	IsActive     bool    `json:"is_active" db:"is_active"`
}

type GetMenuItemFilters struct {
	Id           *string  `json:"id" db:"id"`
	RestaurantId *string  `json:"restaurant_id" db:"restaurant_id"`
	Name         *string  `json:"name" db:"name"`
	PriceMin     *float64 `json:"price_min" db:"price_min"`
	PriceMax     *float64 `json:"price_max" db:"price_max"`
	IsActive     *bool    `json:"is_active" db:"is_active"`
}

func ValidateMenuItem(menuItem *MenuItem) error {
	if menuItem.RestaurantId == "" {
		return errors.New("restaurant id is required")
	}
	if menuItem.Name == "" {
		return errors.New("name is required")
	}
	if menuItem.Price < 0 {
		return errors.New("price must be non-negative")
	}

	return nil
}
