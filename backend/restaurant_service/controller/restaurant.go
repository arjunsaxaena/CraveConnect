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

	menuFile, err := ctx.FormFile("menu_image")
	if err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "menu image is required"})
		return
	}
	menuImagePath, err := utils.SaveMenuImage(menuFile)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save menu"})
		return
	}
	restaurant.MenuPath = menuImagePath

	if err := model.ValidateRestaurant(restaurant); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Create(ctx, restaurant); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	if err := writer.WriteField("restaurant_id", restaurant.Id); err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	src, err := menuFile.Open()
	if err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}
	defer src.Close()

	part, err := writer.CreateFormFile("menu_image", menuFile.Filename)
	if err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	if _, err = io.Copy(part, src); err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	if err = writer.Close(); err != nil {
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Restaurant created but menu processing failed: " + err.Error(),
		})
		return
	}

	req, err := http.NewRequest("POST", DATA_PIPELINE_SERVICE_URL+"/process-menu", body)
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

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		ctx.JSON(http.StatusCreated, gin.H{
			"restaurant": restaurant,
			"warning":    "Data pipeline service returned error: " + string(bodyBytes),
		})
		return
	}

	ctx.JSON(http.StatusCreated, restaurant)
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
