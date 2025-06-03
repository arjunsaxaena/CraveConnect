package model

import (
	"encoding/json"
	"errors"
	"time"

	"github.com/lib/pq"
	"github.com/pgvector/pgvector-go"
)

type MenuItem struct {
	Id           string           `json:"id" db:"id"`
	RestaurantId string           `json:"restaurant_id" db:"restaurant_id"`
	CategoryId   *string           `json:"category_id" db:"category_id"`
	Name         string           `json:"name" db:"name"`
	Description  *string           `json:"description" db:"description"`
	Ingredients  pq.StringArray         `json:"ingredients" db:"ingredients"`
	NutritionalInfo *json.RawMessage `json:"nutritional_info" db:"nutritional_info"`
	Price        float64          `json:"price" db:"price"`
	IsSpicy      bool             `json:"is_spicy" db:"is_spicy"`
	IsVegetarian bool             `json:"is_vegetarian" db:"is_vegetarian"`
	IsAvailable  bool             `json:"is_available" db:"is_available"`
	Sizes        pq.StringArray   `json:"sizes" db:"sizes"`
	Embedding    *pgvector.Vector `json:"embedding" db:"embedding"`
	PopularityScore float64          `json:"popularity_score" db:"popularity_score"`
	Meta         *json.RawMessage `json:"meta" db:"meta"`
	CreatedAt    time.Time        `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time        `json:"updated_at" db:"updated_at"`
}

type GetMenuItemFilters struct {
	Id           *string  `json:"id" db:"id"`
	RestaurantId *string  `json:"restaurant_id" db:"restaurant_id"`
	CategoryId   *string  `json:"category_id" db:"category_id"`
	Name         *string  `json:"name" db:"name"`
	PriceMin     *float64 `json:"price_min" db:"price_min"`
	PriceMax     *float64 `json:"price_max" db:"price_max"`
	IsSpicy      *bool    `json:"is_spicy" db:"is_spicy"`
	IsVegetarian *bool    `json:"is_vegetarian" db:"is_vegetarian"`
	IsAvailable  *bool    `json:"is_available" db:"is_available"`
	PopularityScoreMin *float64 `json:"popularity_score_min" db:"popularity_score_min"`
	PopularityScoreMax *float64 `json:"popularity_score_max" db:"popularity_score_max"`
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
	if menuItem.Sizes == nil {
		menuItem.Sizes = pq.StringArray{"Single size"}
	}
	return nil
}

////////////////////////////////////////////////////////////////////////////////////////////

type MenuCategory struct {
	Id           string           `json:"id" db:"id"`
	RestaurantId string           `json:"restaurant_id" db:"restaurant_id"`
	Name         string           `json:"name" db:"name"`
	Description  *string          `json:"description" db:"description"`
	Meta         *json.RawMessage `json:"meta" db:"meta"`
	CreatedAt    time.Time        `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time        `json:"updated_at" db:"updated_at"`
}

type GetMenuCategoryFilters struct {
	Id           *string  `json:"id" db:"id"`
	RestaurantId *string  `json:"restaurant_id" db:"restaurant_id"`
	Name         *string  `json:"name" db:"name"`
}

func ValidateMenuCategory(menuCategory *MenuCategory) error {
	if menuCategory.RestaurantId == "" {
		return errors.New("restaurant id is required")
	}
	if menuCategory.Name == "" {
		return errors.New("name is required")
	}
	return nil
}
