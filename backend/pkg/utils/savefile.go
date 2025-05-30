package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
)

const (
	RestaurantImagesDir = "../uploads/restaurant_images"
	MenuImagesDir       = "../uploads/menu_images"
	MenuItemImagesDir   = "../uploads/menu_item_images"
)

var FILE_SERVICE_URL = func() string {
	url := os.Getenv("FILE_SERVICE_URL")
	if url == "" {
		return "http://localhost:8005"
	}
	return url
}()

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

func CreateFileRecord(file *multipart.FileHeader, filePath string) (*model.File, error) {
	fileInfo := &model.File{
		Filename: file.Filename,
		FilePath: filePath,
		FileType: filepath.Ext(file.Filename),
		FileSize: file.Size,
		MimeType: file.Header.Get("Content-Type"),
	}

	return fileInfo, model.ValidateFile(fileInfo)
}

func SaveFileToFileService(fileInfo *model.File) (string, error) {
	jsonData, err := json.Marshal(fileInfo)
	if err != nil {
		return "", fmt.Errorf("error marshaling file data: %v", err)
	}

	url := FILE_SERVICE_URL + "/api/files"
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return "", fmt.Errorf("error creating request: %v", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error making request to file service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("file service responded with code %d: %s", resp.StatusCode, string(bodyBytes))
	}

	var fileResponse model.File
	if err := json.NewDecoder(resp.Body).Decode(&fileResponse); err != nil {
		return "", fmt.Errorf("error parsing file service response: %v", err)
	}

	return fileResponse.ID, nil
}

func DeleteFileFromFileService(fileID string) error {
	url := FILE_SERVICE_URL + "/api/files/" + fileID
	req, err := http.NewRequest("DELETE", url, nil)
	if err != nil {
		return fmt.Errorf("error creating delete request: %v", err)
	}

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("error making delete request to file service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("file service responded with code %d: %s", resp.StatusCode, string(bodyBytes))
	}

	return nil
}

func SaveRestaurantImage(file *multipart.FileHeader) (string, error) {
	return SaveFile(file, RestaurantImagesDir)
}

func SaveMenuImage(file *multipart.FileHeader) (string, error) {
	return SaveFile(file, MenuImagesDir)
}
func SaveMenuItemImage(file *multipart.FileHeader) (string, error) {
	return SaveFile(file, MenuItemImagesDir)
}
