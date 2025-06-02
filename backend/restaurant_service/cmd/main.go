package main

import (
	"log"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/arjunsaxaena/CraveConnect.git/backend/restaurant_service/controller"
	"github.com/gin-gonic/gin"
)

func main() {
	database.Connect()
	defer database.Close()

	router := gin.Default()

	restaurantController := controller.NewRestaurantController()

	restaurantRoutes := router.Group("/api/restaurants")
	{
		restaurantRoutes.POST("", restaurantController.CreateRestaurant)
		restaurantRoutes.GET("", restaurantController.GetRestaurants)
		restaurantRoutes.PATCH("", restaurantController.UpdateRestaurant)
		restaurantRoutes.DELETE("/:id", restaurantController.DeleteRestaurant)
	}

	log.Println("Starting restaurant service on port 8003...")
	if err := router.Run(":8003"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
