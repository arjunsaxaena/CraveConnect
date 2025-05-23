package controller

import (
	"fmt"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/menu_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/gin-gonic/gin"
)

type MenuController struct {
	repo *repository.MenuRepository
}

func NewMenuController() *MenuController {
	return &MenuController{
		repo: repository.NewMenuRepository(),
	}
}

func (c *MenuController) CreateMenuItem(ctx *gin.Context) {
	menuItem := &model.MenuItem{}
	if err := ctx.ShouldBind(menuItem); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	imageFile, err := ctx.FormFile("item_image")
	if err == nil {
		itemImagePath, err := utils.SaveMenuItemImage(imageFile)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save image"})
			return
		}
		menuItem.ImagePath = itemImagePath
	}

	if err := model.ValidateMenuItem(menuItem); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Create(ctx, menuItem); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusCreated, menuItem)
}

func (c *MenuController) GetMenuItems(ctx *gin.Context) {
	filters := &model.GetMenuItemFilters{}

	if id := ctx.Query("id"); id != "" {
		filters.Id = &id
	}
	if restaurantId := ctx.Query("restaurant_id"); restaurantId != "" {
		filters.RestaurantId = &restaurantId
	}
	if name := ctx.Query("name"); name != "" {
		filters.Name = &name
	}
	if priceMin := ctx.Query("price_min"); priceMin != "" {
		var min float64
		_, err := fmt.Sscanf(priceMin, "%f", &min)
		if err == nil {
			filters.PriceMin = &min
		}
	}
	if priceMax := ctx.Query("price_max"); priceMax != "" {
		var max float64
		_, err := fmt.Sscanf(priceMax, "%f", &max)
		if err == nil {
			filters.PriceMax = &max
		}
	}
	if size := ctx.Query("size"); size != "" {
		filters.Size = &size
	}
	if isActive := ctx.Query("is_active"); isActive != "" {
		active := isActive == "true"
		filters.IsActive = &active
	}

	menuItems, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, menuItems)
}

func (c *MenuController) UpdateMenuItem(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingItems, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch menu item"})
		return
	}
	if len(existingItems) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "menu item not found"})
		return
	}
	existingItem := existingItems[0]

	updateData := &model.MenuItem{}
	if err := ctx.ShouldBind(updateData); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if updateData.Name != "" {
		existingItem.Name = updateData.Name
	}
	if updateData.Description != "" {
		existingItem.Description = updateData.Description
	}
	if updateData.Price > 0 {
		existingItem.Price = updateData.Price
	}
	if updateData.Size != "" {
		existingItem.Size = updateData.Size
	}
	if updateData.RestaurantId != "" {
		existingItem.RestaurantId = updateData.RestaurantId
	}

	imageFile, err := ctx.FormFile("item_image")
	if err == nil {
		imagePath, err := utils.SaveMenuItemImage(imageFile)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to save image"})
			return
		}
		existingItem.ImagePath = imagePath
	}

	if err := model.ValidateMenuItem(existingItem); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Update(ctx, existingItem); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, existingItem)
}

func (c *MenuController) DeleteMenuItem(ctx *gin.Context) {
	id := ctx.Param("id")
	if err := c.repo.Delete(ctx, id); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, gin.H{"message": "menu item deleted"})
}
