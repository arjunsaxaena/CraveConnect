package controller

import (
	"database/sql"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/user_service/repository"
	"github.com/gin-gonic/gin"
)

type UserAddressController struct {
	repo     *repository.UserAddressRepository
	userRepo *repository.UserRepository
}

func NewUserAddressController() *UserAddressController {
	return &UserAddressController{
		repo:     repository.NewUserAddressRepository(),
		userRepo: repository.NewUserRepository(),
	}
}

func (c *UserAddressController) CreateUserAddress(ctx *gin.Context) {
	address := &model.UserAddress{}
	if err := ctx.ShouldBind(address); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateUserAddress(address); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	users, err := c.userRepo.Get(ctx, address.UserId, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to validate user: " + err.Error()})
		return
	}
	if len(users) == 0 {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "User ID does not exist"})
		return
	}

	if err := c.repo.Create(ctx, address); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if address.IsPrimary {
		user := users[0]
		user.DefaultAddressId = &address.Id
		
		if err := c.userRepo.Update(ctx, user); err != nil {
			ctx.JSON(http.StatusCreated, gin.H{
				"address": address,
				"warning": "Address created but failed to update user's default address: " + err.Error(),
			})
			return
		}
	}

	ctx.JSON(http.StatusCreated, address)
}

func (c *UserAddressController) GetUserAddresses(ctx *gin.Context) {
	filters := &model.GetUserAddressFilters{}
	if id := ctx.Query("id"); id != "" {
		filters.Id = &id
	}
	if userId := ctx.Query("user_id"); userId != "" {
		filters.UserId = &userId
	}
	if postalCode := ctx.Query("postal_code"); postalCode != "" {
		filters.PostalCode = &postalCode
	}
	if isPrimary := ctx.Query("is_primary"); isPrimary != "" {
		primary := isPrimary == "true"
		filters.IsPrimary = &primary
	}
	if isActive := ctx.Query("is_active"); isActive != "" {
		active := isActive == "true"
		filters.IsActive = &active
	}

	addresses, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, addresses)
}

func (c *UserAddressController) UpdateUserAddress(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingAddresses, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch address"})
		return
	}
	if len(existingAddresses) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "address not found"})
		return
	}

	address := existingAddresses[0]
	if err := ctx.ShouldBind(address); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateUserAddress(address); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if address.UserId != existingAddresses[0].UserId {
		users, err := c.userRepo.Get(ctx, address.UserId, nil)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to validate user: " + err.Error()})
			return
		}
		if len(users) == 0 {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "User ID does not exist"})
			return
		}
	}

	if err := c.repo.Update(ctx, address); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	isPrimaryChanged := !existingAddresses[0].IsPrimary && address.IsPrimary
	
	if isPrimaryChanged {
		users, err := c.userRepo.Get(ctx, address.UserId, nil)
		if err != nil {
			ctx.JSON(http.StatusOK, gin.H{
				"address": address,
				"warning": "Address updated but failed to fetch user: " + err.Error(),
			})
			return
		}
		
		if len(users) > 0 {
			user := users[0]
			user.DefaultAddressId = &address.Id
			
			if err := c.userRepo.Update(ctx, user); err != nil {
				ctx.JSON(http.StatusOK, gin.H{
					"address": address,
					"warning": "Address updated but failed to update user's default address: " + err.Error(),
				})
				return
			}
		}
	}

	ctx.JSON(http.StatusOK, address)
}

func (c *UserAddressController) DeleteUserAddress(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingAddresses, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch address"})
		return
	}
	if len(existingAddresses) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "address not found"})
		return
	}

	address := existingAddresses[0]
	userId := address.UserId
	isPrimary := address.IsPrimary

	if err := c.repo.Delete(ctx, id); err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "address not found"})
			return
		}
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if isPrimary {
		users, err := c.userRepo.Get(ctx, userId, nil)
		if err != nil {
			ctx.JSON(http.StatusOK, gin.H{
				"message": "address deleted successfully",
				"warning": "Failed to fetch user to update default address: " + err.Error(),
			})
			return
		}
		
		if len(users) > 0 {
			user := users[0]
			user.DefaultAddressId = nil
			
			if err := c.userRepo.Update(ctx, user); err != nil {
				ctx.JSON(http.StatusOK, gin.H{
					"message": "address deleted successfully",
					"warning": "Failed to update user's default address: " + err.Error(),
				})
				return
			}
		}
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "address deleted successfully"})
}