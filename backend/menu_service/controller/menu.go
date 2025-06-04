package controller

import (
	"encoding/json"
	"fmt"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/menu_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/gin-gonic/gin"
)

type MenuController struct {
	repo *repository.MenuRepository
	categoryRepo *repository.MenuCategoryRepository
}

func NewMenuController() *MenuController {
	return &MenuController{
		repo: repository.NewMenuRepository(),
		categoryRepo: repository.NewMenuCategoryRepository(),
	}
}

func (c *MenuController) CreateMenuItem(ctx *gin.Context) {
	menuItem := &model.MenuItem{}
	if err := ctx.ShouldBind(menuItem); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateMenuItem(menuItem); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	restaurantID := menuItem.RestaurantId
	valid, err := utils.ValidateRestaurant(restaurantID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if !valid {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid restaurant ID"})
		return
	}

	category, err := c.categoryRepo.Get(ctx, *menuItem.CategoryId, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if len(category) == 0 {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
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
	if categoryId := ctx.Query("category_id"); categoryId != "" {
		filters.CategoryId = &categoryId
	}
	if name := ctx.Query("name"); name != "" {
		filters.Name = &name
	}
	
	for key, value := range ctx.Request.URL.Query() {
		if len(key) > 7 && key[:7] == "prices." {
			size := key[7:]
			if len(value) > 0 {
				var price float64
				_, err := fmt.Sscanf(value[0], "%f", &price)
				if err == nil {
					if filters.Prices == nil {
						priceJSON := json.RawMessage(fmt.Sprintf(`{"%s": %f}`, size, price))
						filters.Prices = &priceJSON
					}
				}
			}
		}
	}

	if isSpicy := ctx.Query("is_spicy"); isSpicy != "" {
		isSpicyBool := isSpicy == "true"
		filters.IsSpicy = &isSpicyBool
	}
	if isVegetarian := ctx.Query("is_vegetarian"); isVegetarian != "" {
		isVegetarianBool := isVegetarian == "true"
		filters.IsVegetarian = &isVegetarianBool
	}
	if isAvailable := ctx.Query("is_available"); isAvailable != "" {
		isAvailableBool := isAvailable == "true"
		filters.IsAvailable = &isAvailableBool
	}
	if popularityScoreMin := ctx.Query("popularity_score_min"); popularityScoreMin != "" {
		var min float64
		_, err := fmt.Sscanf(popularityScoreMin, "%f", &min)
		if err == nil {
			filters.PopularityScoreMin = &min
		}
	}
	if popularityScoreMax := ctx.Query("popularity_score_max"); popularityScoreMax != "" {
		var max float64
		_, err := fmt.Sscanf(popularityScoreMax, "%f", &max)
		if err == nil {
			filters.PopularityScoreMax = &max
		}
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
	if updateData.CategoryId != nil {
		category, err := c.categoryRepo.Get(ctx, *updateData.CategoryId, nil)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if len(category) == 0 {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
			return
		}
		existingItem.CategoryId = &category[0].Id
	}
	if updateData.Ingredients != nil {
		existingItem.Ingredients = updateData.Ingredients
	}
	if updateData.NutritionalInfo != nil {
		existingItem.NutritionalInfo = updateData.NutritionalInfo
	}
	if updateData.Description != nil {
		existingItem.Description = updateData.Description
	}
	if updateData.Prices != nil {
		existingItem.Prices = updateData.Prices
	}
	if updateData.RestaurantId != "" {
		existingItem.RestaurantId = updateData.RestaurantId
		valid, err := utils.ValidateRestaurant(updateData.RestaurantId)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if !valid {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid restaurant ID"})
			return
		}
	}
	if updateData.Meta != nil {
		existingItem.Meta = updateData.Meta
	}
	existingItem.IsSpicy = updateData.IsSpicy
	existingItem.IsVegetarian = updateData.IsVegetarian
	existingItem.IsAvailable = updateData.IsAvailable

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
