package model

import (
	"encoding/json"
	"errors"
)

type File struct {
	BaseEntity
	ID       string `json:"id" db:"id"`
	Filename string `json:"filename" db:"filename"`
	FilePath string `json:"file_path" db:"file_path"`
	FileType string `json:"file_type" db:"file_type"`
	FileSize int64  `json:"file_size" db:"file_size"`
	MimeType string `json:"mime_type" db:"mime_type"`
	Meta     *json.RawMessage `json:"meta" db:"meta"`
}

type GetFileFilters struct {
	ID       *string `json:"id" db:"id"`
	Filename *string `json:"filename" db:"filename"`
	FilePath *string `json:"file_path" db:"file_path"`
	FileType *string `json:"file_type" db:"file_type"`
	FileSize *int64  `json:"file_size" db:"file_size"`
	MimeType *string `json:"mime_type" db:"mime_type"`
	IsActive *bool   `json:"is_active" db:"is_active"`
}

func ValidateFile(file *File) error {
	if file.Filename == "" {
		return errors.New("filename is required")
	}
	if file.FilePath == "" {
		return errors.New("file path is required")
	}
	if file.FileType == "" {
		return errors.New("file type is required")
	}
	if file.FileSize <= 0 {
		return errors.New("file size must be greater than 0")
	}
	if file.MimeType == "" {
		return errors.New("mime type is required")
	}

	return nil
}
