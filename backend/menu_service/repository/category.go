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

type MenuCategoryRepository struct {
	db *sqlx.DB
}

func NewMenuCategoryRepository() *MenuCategoryRepository {
	return &MenuCategoryRepository{
		db: database.DB,
	}
}

func (r *MenuCategoryRepository) Create(ctx context.Context, category *model.MenuCategory) error {
	category.Id = uuid.New().String()
	category.CreatedAt = time.Now()
	category.UpdatedAt = time.Now()

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("menu_categories")
	ib.Cols("id", "restaurant_id", "name", "description", "meta", "created_at", "updated_at")
	ib.Values(
		category.Id,
		category.RestaurantId,
		category.Name,
		category.Description,
		category.Meta,
		category.CreatedAt,
		category.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&category.Id)
}

func (r *MenuCategoryRepository) Get(ctx context.Context, id string, filters *model.GetMenuCategoryFilters) ([]*model.MenuCategory, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select("id", "restaurant_id", "name", "description", "meta", "created_at", "updated_at")
	sb.From("menu_categories")

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

	var categories []*model.MenuCategory
	for rows.Next() {
		category := &model.MenuCategory{}
		err := rows.Scan(
			&category.Id,
			&category.RestaurantId,
			&category.Name,
			&category.Description,
			&category.Meta,
			&category.CreatedAt,
			&category.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		categories = append(categories, category)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return categories, nil
}

func (r *MenuCategoryRepository) Update(ctx context.Context, category *model.MenuCategory) error {
	category.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("menu_categories")
	ub.Set(
		ub.Assign("restaurant_id", category.RestaurantId),
		ub.Assign("name", category.Name),
		ub.Assign("description", category.Description),
		ub.Assign("meta", category.Meta),
		ub.Assign("updated_at", category.UpdatedAt),
	)
	ub.Where(ub.Equal("id", category.Id))

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

func (r *MenuCategoryRepository) Delete(ctx context.Context, id string) error {
	ub := sqlbuilder.NewDeleteBuilder()
	ub.DeleteFrom("menu_categories")
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