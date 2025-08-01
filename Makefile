DOCKER_USERNAME = arjunsaxena
IMAGE_NAME = craveconnect-backend
IMAGE_TAG = latest
FULL_IMAGE_NAME = $(DOCKER_USERNAME)/$(IMAGE_NAME):$(IMAGE_TAG)
VM_IP = 20.197.17.86
VM_USER = azureuser
SSH_KEY = ~/.ssh/id_rsa

RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

.PHONY: help build push deploy restart logs clean

help:
	@echo "$(BLUE)CraveConnect Deployment Commands:$(NC)"
	@echo ""
	@echo "$(GREEN)make build$(NC)     - Build Docker image locally"
	@echo "$(GREEN)make push$(NC)      - Push image to Docker Hub"
	@echo "$(GREEN)make deploy$(NC)    - Full deployment: build → push → deploy → restart"
	@echo "$(GREEN)make restart$(NC)   - Restart application on VM"
	@echo "$(GREEN)make logs$(NC)      - View application logs on VM"
	@echo "$(GREEN)make clean$(NC)     - Clean up local Docker images"
	@echo "$(GREEN)make ssh$(NC)       - SSH into VM"
	@echo ""

build:
	@echo "$(YELLOW)Building Docker image...$(NC)"
	@docker build -t $(FULL_IMAGE_NAME) .
	@echo "$(GREEN)Image built successfully: $(FULL_IMAGE_NAME)$(NC)"

push:
	@echo "$(YELLOW)Pushing to Docker Hub...$(NC)"
	@docker push $(FULL_IMAGE_NAME)
	@echo "$(GREEN)Image pushed successfully to Docker Hub$(NC)"

deploy-vm:
	@echo "$(YELLOW)Deploying to VM ($(VM_IP))...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'mkdir -p ~/craveconnect'
	@scp -i $(SSH_KEY) docker-compose.yml $(VM_USER)@$(VM_IP):~/craveconnect/
	@scp -i $(SSH_KEY) .env $(VM_USER)@$(VM_IP):~/craveconnect/ 2>/dev/null || echo "$(YELLOW)No .env file found, using VM's existing .env$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose pull craveconnect-backend'
	@echo "$(GREEN)Deployment files copied to VM and image pulled$(NC)"

restart:
	@echo "$(YELLOW)Restarting application on VM...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose down'
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose up -d'
	@echo "$(GREEN)Application restarted on VM$(NC)"
	@echo "$(BLUE)Application URL: http://$(VM_IP):4001$(NC)"

logs:
	@echo "$(YELLOW)Fetching logs from VM...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose logs -f craveconnect-backend'

ssh:
	@echo "$(YELLOW)Connecting to VM...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP)

deploy: build push deploy-vm restart
	@echo "$(GREEN)Full deployment completed successfully!$(NC)"
	@echo "$(BLUE)Your application is now live at: http://$(VM_IP):4001$(NC)"
	@echo "$(BLUE)API docs at: http://$(VM_IP):4001/docs$(NC)"

clean:
	@echo "$(YELLOW)Cleaning up local Docker images...$(NC)"
	@docker rmi $(FULL_IMAGE_NAME) 2>/dev/null || echo "$(YELLOW)Image not found locally$(NC)"
	@docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

status:
	@echo "$(YELLOW)Checking VM status...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose ps'
	@echo "$(GREEN)Status check completed$(NC)"

quick-deploy:
	@echo "$(YELLOW)Quick deployment (pull latest and restart)...$(NC)"
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose pull craveconnect-backend'
	@ssh -i $(SSH_KEY) $(VM_USER)@$(VM_IP) 'cd ~/craveconnect && docker compose down && docker compose up -d'
	@echo "$(GREEN)Quick deployment completed$(NC)"
	@echo "$(BLUE)Application URL: http://$(VM_IP):4001$(NC)" 