package model

import (
	"encoding/json"
	"errors"
	"time"
)

const(
	FilePurposeRestaurantImage = "restaurant_image"
	FilePurposeMenuImage = "menu_image"
	FilePurposeMenuItemImage = "menu_item_image"
	FilePurposeReviewPhoto = "review_photo"
)

type File struct {
	Id string `json:"id" db:"id"`
	UploaderID string `json:"uploader_id" db:"uploader_id"`
	StoragePath string `json:"storage_path" db:"storage_path"`
	OriginalFilename string `json:"original_filename" db:"original_filename"`
	MimeType string `json:"mime_type" db:"mime_type"`
	FileSize int64 `json:"file_size" db:"file_size"`
	Dimensions json.RawMessage `json:"dimensions" db:"dimensions"`
	Checksum string `json:"checksum" db:"checksum"`
	Purpose string `json:"purpose" db:"purpose"`
	IsPublic bool `json:"is_public" db:"is_public"`
	Meta *json.RawMessage `json:"meta" db:"meta"`
	DeletedAt *time.Time `json:"deleted_at" db:"deleted_at"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

type GetFileFilters struct {
	Id *string `json:"id"`
	UploaderID *string `json:"uploader_id"`
	StoragePath *string `json:"storage_path"`
	OriginalFilename *string `json:"original_filename"`
	MimeType *string `json:"mime_type"`
	FileSize *int64 `json:"file_size"`
	Checksum *string `json:"checksum"`
	Purpose *string `json:"purpose"`
	IsPublic *bool `json:"is_public"`
}

func ValidateFile(file *File) error {
	if file.UploaderID == "" {
		return errors.New("uploader_id is required")
	}
	if file.StoragePath == "" {
		return errors.New("storage_path is required")
	}
	if file.OriginalFilename == "" {
		return errors.New("original_filename is required")
	}
	if file.MimeType == "" {
		return errors.New("mime_type is required")
	}
	if file.FileSize <= 0 {
		return errors.New("file_size must be greater than 0")
	}
	if file.Purpose == "" {
		return errors.New("purpose is required")
	}
	if file.Purpose != FilePurposeRestaurantImage &&
		file.Purpose != FilePurposeMenuImage &&
		file.Purpose != FilePurposeMenuItemImage &&
		file.Purpose != FilePurposeReviewPhoto {
		return errors.New("invalid purpose")
	}
	return nil
}


