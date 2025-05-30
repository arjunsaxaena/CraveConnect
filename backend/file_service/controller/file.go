package controller

import (
	"database/sql"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/file_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
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

func (c *FileController) CreateFile(ctx *gin.Context) {
	file := &model.File{}
	if err := ctx.ShouldBind(file); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateFile(file); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Create(ctx, file); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusCreated, file)
}

func (c *FileController) GetFiles(ctx *gin.Context) {
	filters := &model.GetFileFilters{}
	if id := ctx.Query("id"); id != "" {
		filters.ID = &id
	}
	if filename := ctx.Query("filename"); filename != "" {
		filters.Filename = &filename
	}
	if fileType := ctx.Query("file_type"); fileType != "" {
		filters.FileType = &fileType
	}
	if mimeType := ctx.Query("mime_type"); mimeType != "" {
		filters.MimeType = &mimeType
	}
	if isActive := ctx.Query("is_active"); isActive != "" {
		active := isActive == "true"
		filters.IsActive = &active
	}

	files, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, files)
}

func (c *FileController) UpdateFile(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingFiles, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch file"})
		return
	}
	if len(existingFiles) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "file not found"})
		return
	}

	file := existingFiles[0]
	if err := ctx.ShouldBind(file); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateFile(file); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Update(ctx, file); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, file)
}

func (c *FileController) DeleteFile(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	if err := c.repo.Delete(ctx, id); err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "file not found"})
			return
		}
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "file deleted successfully"})
} 