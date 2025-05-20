package utils

import (
	"fmt"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"
	"time"
)

const (
	RestaurantImagesDir = "../uploads/restaurant_images"
	MenuImagesDir      = "../uploads/menu_images"
)

func SaveFile(file *multipart.FileHeader, directory string) (string, error) {
	if err := os.MkdirAll(directory, 0755); err != nil {
		return "", fmt.Errorf("failed to create directory: %v", err)
	}

	timestamp := time.Now().UnixNano()
	originalFilename := file.Filename
	ext := filepath.Ext(originalFilename)
	filename := fmt.Sprintf("%d%s", timestamp, ext)

	fullPath := filepath.Join(directory, filename)

	src, err := file.Open()
	if err != nil {
		return "", fmt.Errorf("failed to open uploaded file: %v", err)
	}
	defer src.Close()

	dst, err := os.Create(fullPath)
	if err != nil {
		return "", fmt.Errorf("failed to create destination file: %v", err)
	}
	defer dst.Close()

	if _, err := io.Copy(dst, src); err != nil {
		return "", fmt.Errorf("failed to copy file contents: %v", err)
	}

	dirName := filepath.Base(directory)
	return filepath.Join(dirName, filename), nil
}

func SaveRestaurantImage(file *multipart.FileHeader) (string, error) {
	return SaveFile(file, RestaurantImagesDir)
}

func SaveMenuImage(file *multipart.FileHeader) (string, error) {
	return SaveFile(file, MenuImagesDir)
}
