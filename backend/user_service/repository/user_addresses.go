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

type UserAddressRepository struct {
	db *sqlx.DB
}

func NewUserAddressRepository() *UserAddressRepository {
	return &UserAddressRepository{
		db: database.DB,
	}
}

func (r *UserAddressRepository) Create(ctx context.Context, address *model.UserAddress) error {
	address.Id = uuid.New().String()
	address.CreatedAt = time.Now()
	address.UpdatedAt = time.Now()
	address.IsActive = true

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("user_addresses")
	ib.Cols(
		"id", "user_id", "address_line1", "address_line2", "city", "state",
		"postal_code", "country", "alias_name", "geo_point", "is_primary",
		"meta", "is_active", "created_at", "updated_at",
	)
	ib.Values(
		address.Id,
		address.UserId,
		address.AddressLine1,
		address.AddressLine2,
		address.City,
		address.State,
		address.PostalCode,
		address.Country,
		address.AliasName,
		address.GeoPoint,
		address.IsPrimary,
		address.Meta,
		address.IsActive,
		address.CreatedAt,
		address.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&address.Id)
}

func (r *UserAddressRepository) Get(ctx context.Context, id string, filters *model.GetUserAddressFilters) ([]*model.UserAddress, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "user_id", "address_line1", "address_line2", "city", "state",
		"postal_code", "country", "alias_name", "geo_point", "is_primary",
		"meta", "is_active", "created_at", "updated_at",
	)
	sb.From("user_addresses")
	
	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.Id != nil {
			conditions = append(conditions, sb.Equal("id", *filters.Id))
		}
		if filters.UserId != nil {
			conditions = append(conditions, sb.Equal("user_id", *filters.UserId))
		}
		if filters.PostalCode != nil {
			conditions = append(conditions, sb.Equal("postal_code", *filters.PostalCode))
		}
		if filters.IsPrimary != nil {
			conditions = append(conditions, sb.Equal("is_primary", *filters.IsPrimary))
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

	var addresses []*model.UserAddress
	for rows.Next() {
		address := &model.UserAddress{}
		err := rows.Scan(
			&address.Id,
			&address.UserId,
			&address.AddressLine1,
			&address.AddressLine2,
			&address.City,
			&address.State,
			&address.PostalCode,
			&address.Country,
			&address.AliasName,
			&address.GeoPoint,
			&address.IsPrimary,
			&address.Meta,
			&address.IsActive,
			&address.CreatedAt,
			&address.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		addresses = append(addresses, address)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return addresses, nil
}

func (r *UserAddressRepository) Update(ctx context.Context, address *model.UserAddress) error {
	address.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("user_addresses")
	ub.Set(
		ub.Assign("user_id", address.UserId),
		ub.Assign("address_line1", address.AddressLine1),
		ub.Assign("address_line2", address.AddressLine2),
		ub.Assign("city", address.City),
		ub.Assign("state", address.State),
		ub.Assign("postal_code", address.PostalCode),
		ub.Assign("country", address.Country),
		ub.Assign("alias_name", address.AliasName),
		ub.Assign("geo_point", address.GeoPoint),
		ub.Assign("is_primary", address.IsPrimary),
		ub.Assign("meta", address.Meta),
		ub.Assign("is_active", address.IsActive),
		ub.Assign("updated_at", address.UpdatedAt),
	)
	ub.Where(ub.Equal("id", address.Id))

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

func (r *UserAddressRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("user_addresses")
	ub.Set(
		ub.Assign("is_primary", false),
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