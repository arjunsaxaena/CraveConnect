package model

import (
	"errors"

	"github.com/pgvector/pgvector-go"
)

type MenuItem struct {
	Id           string           `json:"id" db:"id" form:"id"`
	BaseEntity
	RestaurantId string           `json:"restaurant_id" db:"restaurant_id" form:"restaurant_id"`
	Name         string           `json:"name" db:"name" form:"name"`
	Description  string           `json:"description" db:"description" form:"description"`
	Price        float64          `json:"price" db:"price" form:"price"`
	Size         string           `json:"size" db:"size" form:"size"`
	ImagePath    string           `json:"image_path" db:"image_path" form:"image_path"`
	Embedding    *pgvector.Vector `json:"-" db:"embedding"`
}

type GetMenuItemFilters struct {
	Id           *string  `json:"id" db:"id"`
	RestaurantId *string  `json:"restaurant_id" db:"restaurant_id"`
	Name         *string  `json:"name" db:"name"`
	PriceMin     *float64 `json:"price_min" db:"price_min"`
	PriceMax     *float64 `json:"price_max" db:"price_max"`
	Size         *string  `json:"size" db:"size"`
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
