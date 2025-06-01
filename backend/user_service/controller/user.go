package controller

import (
	"database/sql"
	"net/http"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
	"github.com/arjunsaxaena/CraveConnect.git/backend/user_service/repository"
	"github.com/gin-gonic/gin"
)

type UserController struct {
	repo *repository.UserRepository
	userAddressRepo *repository.UserAddressRepository
}

func NewUserController() *UserController {
	return &UserController{
		repo: repository.NewUserRepository(),
		userAddressRepo: repository.NewUserAddressRepository(),
	}
}

func (c *UserController) CreateUser(ctx *gin.Context) {
	user := &model.User{}
	if err := ctx.ShouldBind(user); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateUser(user); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if user.DefaultAddressId != nil {
		userAddresses, err := c.userAddressRepo.Get(ctx, *user.DefaultAddressId, nil)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if len(userAddresses) == 0 {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Default address id does not exist"})
			return
		}
	}
	
	if err := c.repo.Create(ctx, user); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusCreated, user)
}

func (c *UserController) GetUsers(ctx *gin.Context) {
	filters := &model.GetUserFilters{}
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

	users, err := c.repo.Get(ctx, "", filters)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	ctx.JSON(http.StatusOK, users)
}

func (c *UserController) UpdateUser(ctx *gin.Context) {
	id := ctx.Query("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	existingUsers, err := c.repo.Get(ctx, id, nil)
	if err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": "failed to fetch user"})
		return
	}
	if len(existingUsers) == 0 {
		ctx.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
		return
	}

	if existingUsers[0].DefaultAddressId != nil {
		userAddresses, err := c.userAddressRepo.Get(ctx, *existingUsers[0].DefaultAddressId, nil)
		if err != nil {
			ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if len(userAddresses) == 0 {
			ctx.JSON(http.StatusBadRequest, gin.H{"error": "Default address id does not exist"})
			return
		}
	}

	user := existingUsers[0]
	if err := ctx.ShouldBind(user); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := model.ValidateUser(user); err != nil {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := c.repo.Update(ctx, user); err != nil {
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, user)
}

func (c *UserController) DeleteUser(ctx *gin.Context) {
	id := ctx.Param("id")
	if id == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{"error": "id is required"})
		return
	}

	if err := c.repo.Delete(ctx, id); err != nil {
		if err == sql.ErrNoRows {
			ctx.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
			return
		}
		ctx.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	ctx.JSON(http.StatusOK, gin.H{"message": "user deleted successfully"})
} 