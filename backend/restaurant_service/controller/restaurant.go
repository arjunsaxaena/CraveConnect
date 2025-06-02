package controller

import (
	"fmt"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/restaurant_service/repository"
	"github.com/gin-gonic/gin"
)

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

	if err := model.ValidateRestaurant(restaurant); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Create(ctx, restaurant); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusCreated, gin.H{
		"restaurant": restaurant,
		"message":    "Restaurant created successfully",
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
	if ownerId := ctx.Query("owner_id"); ownerId != "" {
		filters.OwnerId = &ownerId
	}
	if minRatingStr := ctx.Query("min_rating"); minRatingStr != "" {
		var minRating float64
		if _, err := fmt.Sscanf(minRatingStr, "%f", &minRating); err == nil {
			filters.MinRating = &minRating
		}
	}
	if maxDeliveryFeeStr := ctx.Query("max_delivery_fee"); maxDeliveryFeeStr != "" {
		var maxFee float64
		if _, err := fmt.Sscanf(maxDeliveryFeeStr, "%f", &maxFee); err == nil {
			filters.MaxDeliveryFee = &maxFee
		}
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

	// Update fields if provided in the request
	if updateData.Name != "" {
		existingRestaurant.Name = updateData.Name
	}
	if updateData.Description != nil {
		existingRestaurant.Description = updateData.Description
	}
	if len(updateData.CuisineTypes) > 0 {
		existingRestaurant.CuisineTypes = updateData.CuisineTypes
	}
	if updateData.DeliveryRadiusKm > 0 {
		existingRestaurant.DeliveryRadiusKm = updateData.DeliveryRadiusKm
	}
	if updateData.MinOrderAmount > 0 {
		existingRestaurant.MinOrderAmount = updateData.MinOrderAmount
	}
	if updateData.DeliveryFee > 0 {
		existingRestaurant.DeliveryFee = updateData.DeliveryFee
	}
	if updateData.OperatingHours != nil {
		existingRestaurant.OperatingHours = updateData.OperatingHours
	}
	if updateData.Location != "" {
		existingRestaurant.Location = updateData.Location
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
