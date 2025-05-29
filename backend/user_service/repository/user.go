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

type UserRepository struct {
	db *sqlx.DB
}

func NewUserRepository() *UserRepository {
	return &UserRepository{
		db: database.DB,
	}
}

func (r *UserRepository) Create(ctx context.Context, user *model.User) error {
	user.Id = uuid.New().String()
	user.CreatedAt = time.Now()
	user.UpdatedAt = time.Now()
	user.IsActive = true

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("users")
	ib.Cols(
		"id", "name", "email", "phone", "auth_provider", "meta",
		"is_active", "created_at", "updated_at",
	)
	ib.Values(
		user.Id,
		user.Name,
		user.Email,
		user.Phone,
		user.AuthProvider,
		user.Meta,
		user.IsActive,
		user.CreatedAt,
		user.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&user.Id)
}

func (r *UserRepository) Get(ctx context.Context, id string, filters *model.GetUserFilters) ([]*model.User, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "name", "email", "phone", "auth_provider", "meta",
		"is_active", "created_at", "updated_at",
	)
	sb.From("users")
	
	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.Email != nil {
			conditions = append(conditions, sb.Equal("email", *filters.Email))
		}
		if filters.Phone != nil {
			conditions = append(conditions, sb.Equal("phone", *filters.Phone))
		}
		if filters.AuthProvider != nil {
			conditions = append(conditions, sb.Equal("auth_provider", *filters.AuthProvider))
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

	var users []*model.User
	for rows.Next() {
		user := &model.User{}
		err := rows.Scan(
			&user.Id,
			&user.Name,
			&user.Email,
			&user.Phone,
			&user.AuthProvider,
			&user.Meta,
			&user.IsActive,
			&user.CreatedAt,
			&user.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		users = append(users, user)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return users, nil
}

func (r *UserRepository) Update(ctx context.Context, user *model.User) error {
	user.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("users")
	ub.Set(
		ub.Assign("name", user.Name),
		ub.Assign("email", user.Email),
		ub.Assign("phone", user.Phone),
		ub.Assign("auth_provider", user.AuthProvider),
		ub.Assign("meta", user.Meta),
		ub.Assign("is_active", user.IsActive),
		ub.Assign("updated_at", user.UpdatedAt),
	)
	ub.Where(ub.Equal("id", user.Id))

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

func (r *UserRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("users")
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