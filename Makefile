.PHONY: up down reset logs seed demo rebuild

up:
	docker compose up --build -d

down:
	docker compose down

reset:
	docker compose down -v

logs:
	docker compose logs -f

seed:
	docker compose exec web python seed_demo_data.py

demo:
	make up
	make seed

rebuild:
	docker compose down
	docker compose up --build -d