reload:
	@docker compose down
	@docker compose up -d --build
	@echo open http://localhost:8080
