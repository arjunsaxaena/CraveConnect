package utils

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/arjunsaxaena/CraveConnect.git/backend/pkg/model"
)

var (
	userServiceURL = "http://localhost:8001"
	httpClient     = &http.Client{Timeout: 5 * time.Second}
)

func init() {
	if envURL := os.Getenv("USER_SERVICE_URL"); envURL != "" {
		userServiceURL = envURL
	}
}

func ValidateUser(userID string) (bool, error) {
	if userID == "" {
		return false, errors.New("user ID cannot be empty")
	}

	url := fmt.Sprintf("%s/api/users?id=%s", userServiceURL, userID)
	
	resp, err := httpClient.Get(url)
	if err != nil {
		return false, fmt.Errorf("failed to connect to user service: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return false, fmt.Errorf("user service returned error status: %d", resp.StatusCode)
	}

	var users []model.User
	if err := json.NewDecoder(resp.Body).Decode(&users); err != nil {
		return false, fmt.Errorf("failed to parse user service response: %v", err)
	}

	if len(users) == 0 {
		return false, nil
	}

	return users[0].IsActive, nil
} 