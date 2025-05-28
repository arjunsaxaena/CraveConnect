package controller

import (
	"bytes"
	"io"
	"mime/multipart"
	"net/http"
	"os"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/arjunsaxaena/CraveConnect.git/backend/restaurant_service/repository"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

var _ = godotenv.Load()

var DATA_PIPELINE_SERVICE_URL = func() string {
	url := os.Getenv("DATA_PIPELINE_SERVICE_URL")
	if url == "" {
		return "http://localhost:8003"
	}
	return url
}()

type RestaurantController struct {
	repo *repository.RestaurantRepository
}

func NewRestaurantController() *RestaurantController {
	return &RestaurantController{
		repo: repository.NewRestaurantRepository(),
	}
}

func (c *RestaurantController) CreateRestaurant(ctx *gin.Context) {
	restaurant := &model.Restaurant{}
	if err := ctx.ShouldBind(restaurant); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Save restaurant image (single file)
	imageFile, err := ctx.FormFile("restaurant_image")
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "restaurant image is required"})
		return
	}
	restaurantImagePath, err := utils.SaveRestaurantImage(imageFile)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save image"})
		return
	}
	restaurant.ImagePath = restaurantImagePath

	// Save restaurant to database first
	if err := c.repo.Create(ctx, restaurant); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Process multiple menu images
	form, err := ctx.MultipartForm()
	if err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	// Try both plural and singular field names for backward compatibility
	menuFiles := form.File["menu_images"] // Note the plural name
	if len(menuFiles) == 0 {
		// Fall back to singular name if plural not found
		menuFiles = form.File["menu_image"]
	}

	if len(menuFiles) == 0 {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but no menu images provided",
		})
		return
	}

	// Process menu images
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	// Add restaurant_id field
	if err := writer.WriteField("restaurant_id", restaurant.Id); err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	// Add all menu images to the request
	for _, menuFile := range menuFiles {
		src, err := menuFile.Open()
		if err != nil {
			continue
		}
		defer src.Close()

		part, err := writer.CreateFormFile("menu_images", menuFile.Filename)
		if err != nil {
			continue
		}

		if _, err = io.Copy(part, src); err != nil {
			continue
		}
	}

	if err = writer.Close(); err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	// Send to batch processing endpoint
	req, err := http.NewRequest("POST", DATA_PIPELINE_SERVICE_URL+"/process-menu-batch", body)
	if err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}
	defer resp.Body.Close()

	ctx.JSON(http.StatusCreated, gin.H{
		"restaurant": restaurant,
		"message":    "Restaurant created and menu is being processed",
	})
}

func (c *RestaurantController) GetRestaurants(ctx *gin.Context) {
	filters := &model.GetRestaurantFilters{}
	if id := ctx.Query("id"); id != "" {
		filters.Id = &id
	}
	if name := ctx.Query("name"); name != "" {
		filters.Name = &name
	}
	if email := ctx.Query("email"); email != "" {
		filters.Email = &email
	}
	if phone := ctx.Query("phone"); phone != "" {
		filters.Phone = &phone
	}
	if authProvider := ctx.Query("auth_provider"); authProvider != "" {
		filters.AuthProvider = &authProvider
	}
	if isActive := ctx.Query("is_active"); isActive != "" {
		active := isActive == "true"
		filters.IsActive = &active
	}

	restaurants, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, restaurants)
}

func (c *RestaurantController) UpdateRestaurant(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingRestaurants, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch restaurant"})
		return
	}
	if len(existingRestaurants) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "restaurant not found"})
		return
	}
	existingRestaurant := existingRestaurants[0]

	updateData := &model.Restaurant{}
	if err := ctx.ShouldBind(updateData); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if updateData.Name != "" {
		existingRestaurant.Name = updateData.Name
	}
	if updateData.Email != "" {
		existingRestaurant.Email = updateData.Email
	}
	if updateData.Phone != "" {
		existingRestaurant.Phone = updateData.Phone
	}
	if updateData.AuthProvider != "" {
		existingRestaurant.AuthProvider = updateData.AuthProvider
	}

	imageFile, err := ctx.FormFile("restaurant_image")
	if err == nil {
		imagePath, err := utils.SaveRestaurantImage(imageFile)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save image"})
			return
		}
		existingRestaurant.ImagePath = imagePath
	}

	if err := model.ValidateRestaurant(existingRestaurant); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Update(ctx, existingRestaurant); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, existingRestaurant)
}

func (c *RestaurantController) DeleteRestaurant(ctx *gin.Context) {
	id := ctx.Param("id")
	if err := c.repo.Delete(ctx, id); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, gin.H{"message": "restaurant deleted"})
}
