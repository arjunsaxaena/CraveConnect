package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/google/uuid"
	"github.com/huandu/go-sqlbuilder"
	"github.com/jmoiron/sqlx"
)

type FileRepository struct {
	db *sqlx.DB
}

func NewFileRepository() *FileRepository {
	return &FileRepository{
		db: database.DB,
	}
}

func (r *FileRepository) Create(ctx context.Context, file *model.File) error {
	file.ID = uuid.New().String()
	file.CreatedAt = time.Now()
	file.UpdatedAt = time.Now()
	file.IsActive = true

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("files")
	ib.Cols(
		"id", "filename", "file_path", "file_type", "file_size", "mime_type", "meta",
		"is_active", "created_at", "updated_at",
	)
	ib.Values(
		file.ID,
		file.Filename,
		file.FilePath,
		file.FileType,
		file.FileSize,
		file.MimeType,
		file.Meta,
		file.IsActive,
		file.CreatedAt,
		file.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&file.ID)
}

func (r *FileRepository) Get(ctx context.Context, id string, filters *model.GetFileFilters) ([]*model.File, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "filename", "file_path", "file_type", "file_size", "mime_type", "meta",
		"is_active", "created_at", "updated_at",
	)
	sb.From("files")

	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.ID != nil {
			conditions = append(conditions, sb.Equal("id", *filters.ID))
		}
		if filters.Filename != nil {
			conditions = append(conditions, sb.Equal("filename", *filters.Filename))
		}
		if filters.FileType != nil {
			conditions = append(conditions, sb.Equal("file_type", *filters.FileType))
		}
		if filters.MimeType != nil {
			conditions = append(conditions, sb.Equal("mime_type", *filters.MimeType))
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
		return nil, fmt.Errorf("failed to query files: %w", err)
	}
	defer rows.Close()

	var files []*model.File
	for rows.Next() {
		file := &model.File{}
		err := rows.Scan(
			&file.ID,
			&file.Filename,
			&file.FilePath,
			&file.FileType,
			&file.FileSize,
			&file.MimeType,
			&file.Meta,
			&file.IsActive,
			&file.CreatedAt,
			&file.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan file row: %w", err)
		}
		files = append(files, file)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating file rows: %w", err)
	}

	return files, nil
}

func (r *FileRepository) Update(ctx context.Context, file *model.File) error {
	file.UpdatedAt = time.Now()

	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("files")
	ub.Set(
		ub.Assign("filename", file.Filename),
		ub.Assign("file_path", file.FilePath),
		ub.Assign("file_type", file.FileType),
		ub.Assign("file_size", file.FileSize),
		ub.Assign("mime_type", file.MimeType),
		ub.Assign("meta", file.Meta),
		ub.Assign("is_active", file.IsActive),
		ub.Assign("updated_at", file.UpdatedAt),
	)
	ub.Where(ub.Equal("id", file.ID))

	query, args := ub.BuildWithFlavor(sqlbuilder.PostgreSQL)
	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to update file: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}
	if rowsAffected == 0 {
		return sql.ErrNoRows
	}

	return nil
}

func (r *FileRepository) Delete(ctx context.Context, id string) error {
	now := time.Now()
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("files")
	ub.Set(
		ub.Assign("is_active", false),
		ub.Assign("updated_at", now),
	)
	ub.Where(ub.Equal("id", id))

	query, args := ub.BuildWithFlavor(sqlbuilder.PostgreSQL)
	result, err := r.db.ExecContext(ctx, query, args...)
	if err != nil {
		return fmt.Errorf("failed to delete file: %w", err)
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to get rows affected: %w", err)
	}
	if rowsAffected == 0 {
		return sql.ErrNoRows
	}

	return nil
} 