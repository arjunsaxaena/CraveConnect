package main

import (
	"log"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/arjunsaxaena/CraveConnect.git/backend/user_service/controller"
	"github.com/gin-gonic/gin"
)

func main() {
	database.Connect()
	defer database.Close()

	router := gin.Default()

	userController := controller.NewUserController()
	userAddressController := controller.NewUserAddressController()

	userRoutes := router.Group("/api/users")
	{
		userRoutes.POST("", userController.CreateUser)
		userRoutes.GET("", userController.GetUsers)
		userRoutes.PATCH("", userController.UpdateUser)
		userRoutes.DELETE("/:id", userController.DeleteUser)
	}

	addressRoutes := router.Group("/api/user-addresses")
	{
		addressRoutes.POST("", userAddressController.CreateUserAddress)
		addressRoutes.GET("", userAddressController.GetUserAddresses)
		addressRoutes.PATCH("", userAddressController.UpdateUserAddress)
		addressRoutes.DELETE("/:id", userAddressController.DeleteUserAddress)
	}

	log.Println("Starting user service on port 8001...")
	if err := router.Run(":8001"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}