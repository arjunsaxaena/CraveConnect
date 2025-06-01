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

type FileRepository struct {
	db *sqlx.DB
}

func NewFileRepository() *FileRepository {
	return &FileRepository{
		db: database.DB,
	}
}

func (r *FileRepository) Create(ctx context.Context, file *model.File) error {
	file.Id = uuid.New().String()
	file.CreatedAt = time.Now()
	file.UpdatedAt = time.Now()

	ib := sqlbuilder.NewInsertBuilder()
	ib.InsertInto("files")
	ib.Cols(
		"id", "uploader_id", "storage_path", "original_filename", "mime_type",
		"file_size", "dimensions", "checksum", "purpose", "is_public", "meta",
		"created_at", "updated_at",
	)
	
	ib.Values(
		file.Id,
		file.UploaderID,
		file.StoragePath,
		file.OriginalFilename,
		file.MimeType,
		file.FileSize,
		file.Dimensions,
		file.Checksum,
		file.Purpose,
		file.IsPublic,
		file.Meta,
		file.CreatedAt,
		file.UpdatedAt,
	)
	ib.SQL("RETURNING id")

	query, args := ib.BuildWithFlavor(sqlbuilder.PostgreSQL)
	return r.db.QueryRowContext(ctx, query, args...).Scan(&file.Id)
}

func (r *FileRepository) Get(ctx context.Context, id string, filters *model.GetFileFilters) ([]*model.File, error) {
	sb := sqlbuilder.NewSelectBuilder()
	sb.Select(
		"id", "uploader_id", "storage_path", "original_filename", "mime_type",
		"file_size", "dimensions", "checksum", "purpose", "is_public", "meta",
		"deleted_at", "created_at", "updated_at",
	)
	sb.From("files")
	
	conditions := []string{}

	if id != "" {
		conditions = append(conditions, sb.Equal("id", id))
	}

	if filters != nil {
		if filters.Id != nil {
			conditions = append(conditions, sb.Equal("id", *filters.Id))
		}
		if filters.UploaderID != nil {
			conditions = append(conditions, sb.Equal("uploader_id", *filters.UploaderID))
		}
		if filters.StoragePath != nil {
			conditions = append(conditions, sb.Equal("storage_path", *filters.StoragePath))
		}
		if filters.OriginalFilename != nil {
			conditions = append(conditions, sb.Equal("original_filename", *filters.OriginalFilename))
		}
		if filters.MimeType != nil {
			conditions = append(conditions, sb.Equal("mime_type", *filters.MimeType))
		}
		if filters.FileSize != nil {
			conditions = append(conditions, sb.Equal("file_size", *filters.FileSize))
		}
		if filters.Checksum != nil {
			conditions = append(conditions, sb.Equal("checksum", *filters.Checksum))
		}
		if filters.Purpose != nil {
			conditions = append(conditions, sb.Equal("purpose", *filters.Purpose))
		}
		if filters.IsPublic != nil {
			conditions = append(conditions, sb.Equal("is_public", *filters.IsPublic))
		}
	}

	conditions = append(conditions, sb.IsNull("deleted_at"))

	if len(conditions) > 0 {
		sb.Where(sb.And(conditions...))
	}

	query, args := sb.BuildWithFlavor(sqlbuilder.PostgreSQL)
	rows, err := r.db.QueryContext(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var files []*model.File
	for rows.Next() {
		file := &model.File{}
		
		err := rows.Scan(
			&file.Id,
			&file.UploaderID,
			&file.StoragePath,
			&file.OriginalFilename,
			&file.MimeType,
			&file.FileSize,
			&file.Dimensions,
			&file.Checksum,
			&file.Purpose,
			&file.IsPublic,
			&file.Meta,
			&file.DeletedAt,
			&file.CreatedAt,
			&file.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		
		files = append(files, file)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return files, nil
}

func (r *FileRepository) Delete(ctx context.Context, id string) error {
	ub := sqlbuilder.NewUpdateBuilder()
	ub.Update("files")
	ub.Set(ub.Assign("deleted_at", time.Now()))
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