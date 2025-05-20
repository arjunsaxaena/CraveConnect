package main

import (
	"log"

	"github.com/arjunsaxaena/CraveConnect.git/backend/menu_service/controller"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/gin-gonic/gin"
)

func main() {
	database.Connect()
	defer database.Close()

	router := gin.Default()

	menuController := controller.NewMenuController()

	menuRoutes := router.Group("/api/menu")
	{
		menuRoutes.POST("", menuController.CreateMenuItem)
		menuRoutes.GET("", menuController.GetMenuItems)
		menuRoutes.GET("/restaurant/:id", menuController.GetMenuItemsByRestaurant)
		menuRoutes.PATCH("", menuController.UpdateMenuItem)
		menuRoutes.DELETE("/:id", menuController.DeleteMenuItem)
	}

	log.Println("Starting menu service on port 8002...")
	if err := router.Run(":8002"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
