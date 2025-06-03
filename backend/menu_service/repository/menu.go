package repository

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"time"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/google/uuid"
	"github.com/huandu/go-sqlbuilder"
	"github.com/jmoiron/sqlx"
)

type MenuRepository struct {
	db *sqlx.DB
}

func NewMenuRepository() *MenuRepository {
	return &MenuRepository{
		db: database.DB,
	}
}

func (r *MenuRepository) Create(ctx context.Context, menuItem *model.MenuItem) error {
	menuItem.Id = uuid.New().String()
	menuItem.CreatedAt = time.Now()
	menuItem.UpdatedAt = time.Now()

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("menu_items")
	ib.Cols(
		"id", "restaurant_id", "category_id", "name", "description", "ingredients", 
		"nutritional_info", "prices", "is_spicy", "is_vegetarian", "is_available", 
		"popularity_score", "meta", "created_at", "updated_at", "embedding",
	)
	ib.Values(
		menuItem.Id,
		menuItem.RestaurantId,
		menuItem.CategoryId,
		menuItem.Name,
		menuItem.Description,
		menuItem.Ingredients,
		menuItem.NutritionalInfo,
		menuItem.Prices,
		menuItem.IsSpicy,
		menuItem.IsVegetarian,
		menuItem.IsAvailable,
		menuItem.PopularityScore,
		menuItem.Meta,
		menuItem.CreatedAt,
		menuItem.UpdatedAt,
		menuItem.Embedding,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&menuItem.Id)
}

func (r *MenuRepository) Get(ctx context.Context, id string, filters *model.GetMenuItemFilters) ([]*model.MenuItem, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "restaurant_id", "category_id", "name", "description", "ingredients", 
		"nutritional_info", "prices", "is_spicy", "is_vegetarian", "is_available", 
		"popularity_score", "meta", "created_at", "updated_at", "embedding",
	)
	sb.From("menu_items")

	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.Id != nil {
			conditions = append(conditions, sb.Equal("id", *filters.Id))
		}
		if filters.RestaurantId != nil {
			conditions = append(conditions, sb.Equal("restaurant_id", *filters.RestaurantId))
		}
		if filters.CategoryId != nil {
			conditions = append(conditions, sb.Equal("category_id", *filters.CategoryId))
		}
		if filters.Name != nil {
			conditions = append(conditions, sb.Like("name", "%"+*filters.Name+"%"))
		}
		if filters.Prices != nil {
			var pricesMap map[string]float64
			if err := json.Unmarshal(*filters.Prices, &pricesMap); err == nil {
				for size, price := range pricesMap {
					conditions = append(conditions, fmt.Sprintf("(prices->>'%s')::float = %f", size, price))
				}
			}
		}
		if filters.PriceMin != nil {
			conditions = append(conditions, fmt.Sprintf("EXISTS (SELECT 1 FROM jsonb_each_text(prices) WHERE (value)::float >= %f)", *filters.PriceMin)) // What The Fuck idk
		}
		if filters.PriceMax != nil {
			conditions = append(conditions, fmt.Sprintf("EXISTS (SELECT 1 FROM jsonb_each_text(prices) WHERE (value)::float <= %f)", *filters.PriceMax)) // What The Fuck idk
		}
		if filters.IsSpicy != nil {
			conditions = append(conditions, sb.Equal("is_spicy", *filters.IsSpicy))
		}
		if filters.IsVegetarian != nil {
			conditions = append(conditions, sb.Equal("is_vegetarian", *filters.IsVegetarian))
		}
		if filters.IsAvailable != nil {
			conditions = append(conditions, sb.Equal("is_available", *filters.IsAvailable))
		}
		if filters.PopularityScoreMin != nil {
			conditions = append(conditions, sb.GreaterEqualThan("popularity_score", *filters.PopularityScoreMin))
		}
		if filters.PopularityScoreMax != nil {
			conditions = append(conditions, sb.LessEqualThan("popularity_score", *filters.PopularityScoreMax))
		}
	}

	if len(conditions) > 0 {
		sb.Where(sb.And(conditions...))
	}

	query, args := sb.BuildWithFlavor(sqlbuilder.PostgreSQL)
	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var menuItems []*model.MenuItem
	for rows.Next() {
		menuItem := &model.MenuItem{}
		err := rows.Scan(
			&menuItem.Id,
			&menuItem.RestaurantId,
			&menuItem.CategoryId,
			&menuItem.Name,
			&menuItem.Description,
			&menuItem.Ingredients,
			&menuItem.NutritionalInfo,
			&menuItem.Prices,
			&menuItem.IsSpicy,
			&menuItem.IsVegetarian,
			&menuItem.IsAvailable,
			&menuItem.PopularityScore,
			&menuItem.Meta,
			&menuItem.CreatedAt,
			&menuItem.UpdatedAt,
			&menuItem.Embedding,
		)
		if err != nil {
			return nil, err
		}
		menuItems = append(menuItems, menuItem)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return menuItems, nil
}

func (r *MenuRepository) Update(ctx context.Context, menuItem *model.MenuItem) error {
	menuItem.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("menu_items")
	ub.Set(
		ub.Assign("restaurant_id", menuItem.RestaurantId),
		ub.Assign("category_id", menuItem.CategoryId),
		ub.Assign("name", menuItem.Name),
		ub.Assign("description", menuItem.Description),
		ub.Assign("ingredients", menuItem.Ingredients),
		ub.Assign("nutritional_info", menuItem.NutritionalInfo),
		ub.Assign("prices", menuItem.Prices),
		ub.Assign("is_spicy", menuItem.IsSpicy),
		ub.Assign("is_vegetarian", menuItem.IsVegetarian),
		ub.Assign("is_available", menuItem.IsAvailable),
		ub.Assign("popularity_score", menuItem.PopularityScore),
		ub.Assign("meta", menuItem.Meta),
		ub.Assign("updated_at", menuItem.UpdatedAt),
		ub.Assign("embedding", menuItem.Embedding),
	)
	ub.Where(ub.Equal("id", menuItem.Id))

	query, args := ub.BuildWithFlavor(sqlbuilder.PostgreSQL)
	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if rowsAffected == 0 {
		return sql.ErrNoRows
	}
	return nil
}

func (r *MenuRepository) Delete(ctx context.Context, id string) error {
	ub := sqlbuilder.NewDeleteBuilder()
	ub.DeleteFrom("menu_items")
	ub.Where(ub.Equal("id", id))

	query, args := ub.BuildWithFlavor(sqlbuilder.PostgreSQL)
	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if rowsAffected == 0 {
		return sql.ErrNoRows
	}
	return nil
}
