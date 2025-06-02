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
	"github.com/lib/pq"
)

type RestaurantRepository struct {
	db *sqlx.DB
}

func NewRestaurantRepository() *RestaurantRepository {
	return &RestaurantRepository{
		db: database.DB,
	}
}

func (r *RestaurantRepository) Create(ctx context.Context, restaurant *model.Restaurant) error {
	restaurant.Id = uuid.New().String()
	restaurant.CreatedAt = time.Now()
	restaurant.UpdatedAt = time.Now()
	restaurant.IsActive = true

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("restaurants")
	ib.Cols(
		"id", "name", "owner_id", "description", "cuisine_types",
		"rating", "delivery_radius_km",
		"min_order_amount", "delivery_fee", "operating_hours",
		"location", "meta", "is_active", "created_at", "updated_at",
	)
	ib.Values(
		restaurant.Id,
		restaurant.Name,
		restaurant.OwnerId,
		restaurant.Description,
		pq.Array(restaurant.CuisineTypes),
		restaurant.Rating,
		restaurant.DeliveryRadiusKm,
		restaurant.MinOrderAmount,
		restaurant.DeliveryFee,
		restaurant.OperatingHours,
		restaurant.Location,
		restaurant.Meta,
		restaurant.IsActive,
		restaurant.CreatedAt,
		restaurant.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&restaurant.Id)
}

func (r *RestaurantRepository) Get(ctx context.Context, id string, filters *model.GetRestaurantFilters) ([]*model.Restaurant, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "name", "owner_id", "description", "cuisine_types",
		"rating", "delivery_radius_km",
		"min_order_amount", "delivery_fee", "operating_hours",
		"location", "meta", "is_active", "created_at", "updated_at",
	)
	sb.From("restaurants")

	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.Name != nil {
			conditions = append(conditions, sb.Equal("name", *filters.Name))
		}
		if filters.OwnerId != nil {
			conditions = append(conditions, sb.Equal("owner_id", *filters.OwnerId))
		}
		if filters.CuisineTypes != nil {
			conditions = append(conditions, sb.Equal("cuisine_types", *filters.CuisineTypes))
		}
		if filters.MinRating != nil {
			conditions = append(conditions, sb.GE("rating", *filters.MinRating))
		}
		if filters.MaxDeliveryFee != nil {
			conditions = append(conditions, sb.LE("delivery_fee", *filters.MaxDeliveryFee))
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

	var restaurants []*model.Restaurant
	for rows.Next() {
		restaurant := &model.Restaurant{}
		var cuisineTypesArray []string
		err := rows.Scan(
			&restaurant.Id,
			&restaurant.Name,
			&restaurant.OwnerId,
			&restaurant.Description,
			pq.Array(&cuisineTypesArray),
			&restaurant.Rating,
			&restaurant.DeliveryRadiusKm,
			&restaurant.MinOrderAmount,
			&restaurant.DeliveryFee,
			&restaurant.OperatingHours,
			&restaurant.Location,
			&restaurant.Meta,
			&restaurant.IsActive,
			&restaurant.CreatedAt,
			&restaurant.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		restaurant.CuisineTypes = cuisineTypesArray

		restaurants = append(restaurants, restaurant)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return restaurants, nil
}

func (r *RestaurantRepository) Update(ctx context.Context, restaurant *model.Restaurant) error {
	restaurant.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("restaurants")
	ub.Set(
		ub.Assign("name", restaurant.Name),
		ub.Assign("owner_id", restaurant.OwnerId),
		ub.Assign("description", restaurant.Description),
		ub.Assign("cuisine_types", pq.Array(restaurant.CuisineTypes)),
		ub.Assign("rating", restaurant.Rating),
		ub.Assign("delivery_radius_km", restaurant.DeliveryRadiusKm),
		ub.Assign("min_order_amount", restaurant.MinOrderAmount),
		ub.Assign("delivery_fee", restaurant.DeliveryFee),
		ub.Assign("operating_hours", restaurant.OperatingHours),
		ub.Assign("meta", restaurant.Meta),
		ub.Assign("is_active", restaurant.IsActive),
		ub.Assign("updated_at", restaurant.UpdatedAt),
	)
	ub.Where(ub.Equal("id", restaurant.Id))

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

func (r *RestaurantRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("restaurants")
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
