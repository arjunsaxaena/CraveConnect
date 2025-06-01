package controller

import (
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"encoding/json"
	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"net/http"
	"strings"

	"github.com/arjunsaxaena/CraveConnect.git/backend/file_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/gin-gonic/gin"
)

type FileController struct {
	repo *repository.FileRepository
}

func NewFileController() *FileController {
	return &FileController{
		repo: repository.NewFileRepository(),
	}
}

func (c *FileController) UploadFile(ctx *gin.Context) {
	file, err := ctx.FormFile("file")
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "File is required"})
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

	src, err := file.Open()
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file"})
		return
	}
	defer src.Close()

	hasher := sha256.New()
	if _, err := io.Copy(hasher, src); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to calculate checksum"})
		return
	}
	checksum := hex.EncodeToString(hasher.Sum(nil))

	existingFile, err := c.repo.Get(ctx, "", &model.GetFileFilters{Checksum: &checksum})
	if err != nil && err != sql.ErrNoRows {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check for duplicate files"})
		return
	}

	if existingFile != nil {
		ctx.JSON(http.StatusOK, gin.H{
			"message": "File already exists",
			"file": existingFile,
		})
		return
	}

	var storagePath string
	var isPublic bool = true
	if publicParam := ctx.PostForm("is_public"); publicParam != "" {
		isPublic = publicParam == "true"
	}

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
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid purpose"})
		return
	}

	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if _, err = src.Seek(0, io.SeekStart); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
		return
	}

	meta := json.RawMessage(`{}`)
	var dimensions json.RawMessage = json.RawMessage(`{}`)

	if strings.HasPrefix(file.Header.Get("Content-Type"), "image/") {
		if _, err = src.Seek(0, io.SeekStart); err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
			return
		}

		img, _, err := image.DecodeConfig(src)
		if err == nil {
			dimensionsJSON := map[string]int{
				"width":  img.Width,
				"height": img.Height,
			}
			dimensions, err = json.Marshal(dimensionsJSON)
			if err != nil {
				ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to process image dimensions"})
				return
			}
		}

		if _, err = src.Seek(0, io.SeekStart); err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to read file"})
			return
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
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Create(ctx, fileModel); err != nil {
    	ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file metadata: " + err.Error()})
    	return
	}

	ctx.JSON(http.StatusCreated, fileModel)
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