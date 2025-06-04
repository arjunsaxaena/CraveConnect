package main

import (
	"log"

	"github.com/arjunsaxaena/CraveConnect.git/backend/file_service/controller"
	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/database"
	"github.com/gin-gonic/gin"
)

func main() {
	database.Connect()
	defer database.Close()

	router := gin.Default()

	fileController := controller.NewFileController()

	fileRoutes := router.Group("/api/files")
	{
		fileRoutes.POST("/upload", fileController.UploadFile)
		fileRoutes.GET("", fileController.GetFiles)
		fileRoutes.DELETE("/:id", fileController.DeleteFile) // TODO: Delete route not deleting file from directory maybe some path issue
	}

	log.Println("Starting file service on port 8004...")
	if err := router.Run(":8004"); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}