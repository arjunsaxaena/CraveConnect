package controller

import (
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/menu_service/repository"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/utils"
	"github.com/gin-gonic/gin"
)

type MenuCategoryController struct {
	repo *repository.MenuCategoryRepository
}

func NewMenuCategoryController() *MenuCategoryController {
	return &MenuCategoryController{
		repo: repository.NewMenuCategoryRepository(),
	}
}

func (c *MenuCategoryController) CreateCategory(ctx *gin.Context) {
	category := &model.MenuCategory{}
	if err := ctx.ShouldBind(category); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateMenuCategory(category); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	restaurantID := category.RestaurantId
	valid, err := utils.ValidateRestaurant(restaurantID)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if !valid {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "Invalid restaurant ID"})
		return
	}

	if err := c.repo.Create(ctx, category); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusCreated, category)
}

func (c *MenuCategoryController) GetCategories(ctx *gin.Context) {
	filters := &model.GetMenuCategoryFilters{}

	if id := ctx.Query("id"); id != "" {
		filters.Id = &id
	}
	if restaurantId := ctx.Query("restaurant_id"); restaurantId != "" {
		filters.RestaurantId = &restaurantId
	}
	if name := ctx.Query("name"); name != "" {
		filters.Name = &name
	}

	categories, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, categories)
}

func (c *MenuCategoryController) UpdateCategory(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingCategories, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch category"})
		return
	}
	if len(existingCategories) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "category not found"})
		return
	}
	existingCategory := existingCategories[0]

	updateData := &model.MenuCategory{}
	if err := ctx.ShouldBind(updateData); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if updateData.Name != "" {
		existingCategory.Name = updateData.Name
	}
	if updateData.Description != nil {
		existingCategory.Description = updateData.Description
	}
	if updateData.RestaurantId != "" {
		existingCategory.RestaurantId = updateData.RestaurantId
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
		existingCategory.Meta = updateData.Meta
	}

	if err := model.ValidateMenuCategory(existingCategory); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Update(ctx, existingCategory); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, existingCategory)
}

func (c *MenuCategoryController) DeleteCategory(ctx *gin.Context) {
	id := ctx.Param("id")
	if err := c.repo.Delete(ctx, id); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, gin.H{"message": "category deleted"})
} 