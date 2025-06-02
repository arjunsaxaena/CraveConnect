package model

import (
	"encoding/json"
	"errors"
)

type Restaurant struct {
	BaseEntity
	Id               string          `json:"id" db:"id"`
	OwnerId          string          `json:"owner_id" db:"owner_id"`
	Name             string          `json:"name" db:"name"`
	Description      *string         `json:"description" db:"description"`
	CuisineTypes     []string        `json:"cuisine_types" db:"cuisine_types"`
	Rating           float64         `json:"rating" db:"rating"`
	DeliveryRadiusKm float64         `json:"delivery_radius_km" db:"delivery_radius_km"`
	MinOrderAmount   float64         `json:"min_order_amount" db:"min_order_amount"`
	DeliveryFee      float64         `json:"delivery_fee" db:"delivery_fee"`
	OperatingHours   json.RawMessage `json:"operating_hours" db:"operating_hours"`
	Location         string          `json:"location" db:"location"`
}

type GetRestaurantFilters struct {
	Id             *string   `json:"id" db:"id"`
	OwnerId        *string   `json:"owner_id" db:"owner_id"`
	Name           *string   `json:"name" db:"name"`
	CuisineTypes   *[]string `json:"cuisine_types" db:"cuisine_types"`
	MinRating      *float64  `json:"min_rating" db:"min_rating"`
	MaxDeliveryFee *float64  `json:"max_delivery_fee" db:"max_delivery_fee"`
	MaxPrepTime    *int      `json:"max_prep_time" db:"max_prep_time"`
	IsActive       *bool     `json:"is_active" db:"is_active"`
}

func ValidateRestaurant(restaurant *Restaurant) error {
	if restaurant.OwnerId == "" {
		return errors.New("owner_id is required")
	}

	if restaurant.Name == "" {
		return errors.New("name is required")
	}

	if len(restaurant.CuisineTypes) == 0 {
		return errors.New("cuisine_types are required")
	}

	if restaurant.OperatingHours == nil {
		return errors.New("operating_hours are required")
	}

	if restaurant.Location == "" {
		return errors.New("location is required")
	}

	return nil
}
