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

	userRoutes := router.Group("/api/users")
	{
		userRoutes.POST("", userController.CreateUser)
		userRoutes.GET("", userController.GetUsers)
		userRoutes.PATCH("", userController.UpdateUser)
		userRoutes.DELETE("/:id", userController.DeleteUser)
	}

	log.Println("Starting user service on port 8004...")
	if err := router.Run(":8004"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}