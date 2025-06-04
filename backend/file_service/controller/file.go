package controller

import (
	"bytes"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"mime/multipart"
	"net/http"
	"strings"

	"github.com/arjunsaxaena/CraveConnect.git/backend/file_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/gin-gonic/gin"
)

const (
	EmbeddingServiceURL = "http://localhost:8005" // Update this with your embedding service URL
)

type FileController struct {
	repo *repository.FileRepository
}

func NewFileController() *FileController {
	return &FileController{
		repo: repository.NewFileRepository(),
	}
}

func (c *FileController) processMenuImage(file *multipart.FileHeader, restaurantID string) error {
	src, err := file.Open()
	if err != nil {
		return err
	}
	defer src.Close()

	// Create a new multipart form
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Add the file
	part, err := writer.CreateFormFile("menu_image", file.Filename)
	if err != nil {
		return err
	}

	if _, err = io.Copy(part, src); err != nil {
		return err
	}

	// Add restaurant_id
	if err = writer.WriteField("restaurant_id", restaurantID); err != nil {
		return err
	}

	// Close the writer
	if err = writer.Close(); err != nil {
		return err
	}

	// Create the request
	req, err := http.NewRequest("POST", EmbeddingServiceURL+"/process-menu", body)
	if err != nil {
		return err
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	// Send the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("embedding service returned status code: %d", resp.StatusCode)
	}

	return nil
}

func (c *FileController) UploadFile(ctx *gin.Context) {
	form, err := ctx.MultipartForm()
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid form data"})
		return
	}

	files := form.File["files"]
	if len(files) == 0 {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "No files provided"})
		return
	}

	uploaderID := ctx.PostForm("uploader_id")
	if uploaderID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Uploader ID is required"})
		return
	}

	isValidUser, err := utils.ValidateUser(uploaderID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to validate user: " + err.Error()})
		return
	}
	if !isValidUser {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid or inactive user ID"})
		return
	}

	purpose := ctx.PostForm("purpose")
	if purpose == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Purpose is required"})
		return
	}

	restaurantID := ctx.PostForm("restaurant_id")
	if purpose == model.FilePurposeMenuImage && restaurantID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Restaurant ID is required for menu images"})
		return
	}

	var isPublic bool = true
	if publicParam := ctx.PostForm("is_public"); publicParam != "" {
		isPublic = publicParam == "true"
	}

	var uploadedFiles []*model.File
	var errors []string

	for _, file := range files {
		src, err := file.Open()
		if err != nil {
			errors = append(errors, "Failed to open file: "+file.Filename)
			continue
		}

		hasher := sha256.New()
		if _, err := io.Copy(hasher, src); err != nil {
			src.Close()
			errors = append(errors, "Failed to calculate checksum for: "+file.Filename)
			continue
		}
		checksum := hex.EncodeToString(hasher.Sum(nil))

		existingFile, err := c.repo.Get(ctx, "", &model.GetFileFilters{Checksum: &checksum})
		if err != nil && err != sql.ErrNoRows {
			src.Close()
			errors = append(errors, "Failed to check for duplicate files: "+file.Filename)
			continue
		}

		if len(existingFile) > 0 {
			uploadedFiles = append(uploadedFiles, existingFile[0])
			src.Close()
			continue
		}

		var storagePath string
		switch purpose {
		case model.FilePurposeRestaurantImage:
			storagePath, err = utils.SaveRestaurantImage(file)
		case model.FilePurposeMenuImage:
			storagePath, err = utils.SaveMenuImage(file)
		case model.FilePurposeMenuItemImage:
			storagePath, err = utils.SaveMenuItemImage(file)
		case model.FilePurposeReviewPhoto:
			storagePath, err = utils.SaveReviewPhoto(file)
		default:
			src.Close()
			errors = append(errors, "Invalid purpose for file: "+file.Filename)
			continue
		}

		if err != nil {
			src.Close()
			errors = append(errors, "Failed to save file: "+file.Filename)
			continue
		}

		if _, err = src.Seek(0, io.SeekStart); err != nil {
			src.Close()
			errors = append(errors, "Failed to read file: "+file.Filename)
			continue
		}

		meta := json.RawMessage(`{}`)
		var dimensions json.RawMessage = json.RawMessage(`{}`)

		if strings.HasPrefix(file.Header.Get("Content-Type"), "image/") {
			if _, err = src.Seek(0, io.SeekStart); err != nil {
				src.Close()
				errors = append(errors, "Failed to read file: "+file.Filename)
				continue
			}

			img, _, err := image.DecodeConfig(src)
			if err == nil {
				dimensionsJSON := map[string]int{
					"width":  img.Width,
					"height": img.Height,
				}
				dimensions, err = json.Marshal(dimensionsJSON)
				if err != nil {
					src.Close()
					errors = append(errors, "Failed to process image dimensions for: "+file.Filename)
					continue
				}
			}

			if _, err = src.Seek(0, io.SeekStart); err != nil {
				src.Close()
				errors = append(errors, "Failed to read file: "+file.Filename)
				continue
			}
		}

		fileModel := &model.File{
			UploaderID:       uploaderID,
			StoragePath:      storagePath,
			OriginalFilename: file.Filename,
			MimeType:         file.Header.Get("Content-Type"),
			FileSize:         file.Size,
			Checksum:         checksum,
			Purpose:          purpose,
			IsPublic:         isPublic,
			Dimensions:       dimensions,
			Meta:             &meta,
		}

		if err := model.ValidateFile(fileModel); err != nil {
			src.Close()
			errors = append(errors, "Invalid file data for: "+file.Filename)
			continue
		}

		if err := c.repo.Create(ctx, fileModel); err != nil {
			src.Close()
			errors = append(errors, "Failed to save file metadata for: "+file.Filename)
			continue
		}

		if purpose == model.FilePurposeMenuImage {
			if err := c.processMenuImage(file, restaurantID); err != nil {
				errors = append(errors, "Failed to process menu image through embedding service: "+file.Filename)
			}
		}

		uploadedFiles = append(uploadedFiles, fileModel)
		src.Close()
	}

	response := gin.H{
		"uploaded_files": uploadedFiles,
	}
	if len(errors) > 0 {
		response["errors"] = errors
	}

	if len(uploadedFiles) > 0 {
		ctx.JSON(http.StatusCreated, response)
	} else {
		ctx.JSON(http.StatusBadRequest, response)
	}
}

func (c *FileController) GetFiles(ctx *gin.Context) {
	filters := &model.GetFileFilters{}
	
	if id := ctx.Query("id"); id != "" {
		filters.Id = &id
	}
	if uploaderID := ctx.Query("uploader_id"); uploaderID != "" {
		filters.UploaderID = &uploaderID
	}
	if storagePath := ctx.Query("storage_path"); storagePath != "" {
		filters.StoragePath = &storagePath
	}
	if originalFilename := ctx.Query("original_filename"); originalFilename != "" {
		filters.OriginalFilename = &originalFilename
	}
	if mimeType := ctx.Query("mime_type"); mimeType != "" {
		filters.MimeType = &mimeType
	}
	if purpose := ctx.Query("purpose"); purpose != "" {
		filters.Purpose = &purpose
	}
	if isPublic := ctx.Query("is_public"); isPublic != "" {
		public := isPublic == "true"
		filters.IsPublic = &public
	}

	files, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, files)
}

func (c *FileController) DeleteFile(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "ID is required"})
		return
	}

	files, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if len(files) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "File not found"})
		return
	}

	file := files[0]

	if err := c.repo.Delete(ctx, id); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete file metadata"})
		return
	}

	var deleteErr error
	switch file.Purpose {
	case model.FilePurposeRestaurantImage:
		deleteErr = utils.DeleteRestaurantImage(file.StoragePath)
	case model.FilePurposeMenuImage:
		deleteErr = utils.DeleteMenuImage(file.StoragePath)
	case model.FilePurposeMenuItemImage:
		deleteErr = utils.DeleteMenuItemImage(file.StoragePath)
	case model.FilePurposeReviewPhoto:
		deleteErr = utils.DeleteReviewPhoto(file.StoragePath)
	}

	if deleteErr != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"error": "File metadata deleted, but failed to delete physical file: " + deleteErr.Error(),
		})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "File deleted successfully"})
} 