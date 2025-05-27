package repository

import (
	"context"
	"database/sql"
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
	menuItem.IsActive = true

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("menu_items")
	ib.Cols(
		"id", "restaurant_id", "name", "description", "price", "size", "image_path", "meta",
		"is_active", "created_at", "updated_at", "embedding",
	)
	ib.Values(
		menuItem.Id,
		menuItem.RestaurantId,
		menuItem.Name,
		menuItem.Description,
		menuItem.Price,
		menuItem.Size,
		menuItem.ImagePath,
		menuItem.Meta,
		menuItem.IsActive,
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
		"id", "restaurant_id", "name", "description", "price", "size", "image_path", "meta",
		"is_active", "created_at", "updated_at", "embedding",
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
		if filters.Name != nil {
			conditions = append(conditions, sb.Like("name", "%"+*filters.Name+"%"))
		}
		if filters.PriceMin != nil {
			conditions = append(conditions, sb.GreaterEqualThan("price", *filters.PriceMin))
		}
		if filters.PriceMax != nil {
			conditions = append(conditions, sb.LessEqualThan("price", *filters.PriceMax))
		}
		if filters.Size != nil {
			conditions = append(conditions, sb.Equal("size", *filters.Size))
		}
		if filters.IsActive != nil {
			conditions = append(conditions, sb.Equal("is_active", *filters.IsActive))
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
			&menuItem.Name,
			&menuItem.Description,
			&menuItem.Price,
			&menuItem.Size,
			&menuItem.ImagePath,
			&menuItem.Meta,
			&menuItem.IsActive,
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
		ub.Assign("name", menuItem.Name),
		ub.Assign("description", menuItem.Description),
		ub.Assign("price", menuItem.Price),
		ub.Assign("size", menuItem.Size),
		ub.Assign("image_path", menuItem.ImagePath),
		ub.Assign("meta", menuItem.Meta),
		ub.Assign("is_active", menuItem.IsActive),
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
	now := time.Now()
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("menu_items")
	ub.Set(
		ub.Assign("is_active", false),
		ub.Assign("updated_at", now),
	)
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
