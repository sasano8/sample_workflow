reload:
	@docker compose down
	@docker compose up -d
	@echo open http://localhost:8080
