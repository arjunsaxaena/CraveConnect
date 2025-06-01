package utils

import (
	"fmt"
	"os"
	"path/filepath"
)

func DeleteFile(storagePath string) error {
	cwd, err := os.Getwd()
	if err != nil {
		return fmt.Errorf("failed to get current directory: %v", err)
	}

	fullPath := filepath.Join(cwd, "backend", storagePath)
	
	if _, err := os.Stat(fullPath); os.IsNotExist(err) {
		return fmt.Errorf("file does not exist: %s", fullPath)
	}
	
	if err := os.Remove(fullPath); err != nil {
		return fmt.Errorf("failed to delete file: %v", err)
	}
	
	return nil
}

func DeleteRestaurantImage(filename string) error {
	return DeleteFile(filepath.Join("uploads/restaurant_images", filename))
}

func DeleteMenuImage(filename string) error {
	return DeleteFile(filepath.Join("uploads/menu_images", filename))
}

func DeleteMenuItemImage(filename string) error {
	return DeleteFile(filepath.Join("uploads/menu_item_images", filename))
}

func DeleteReviewPhoto(filename string) error {
	return DeleteFile(filepath.Join("uploads/review_photos", filename))
} 