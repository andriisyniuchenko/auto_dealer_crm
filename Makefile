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
	@echo "Waiting for web service to be ready..."
	@until docker compose exec web python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" > /dev/null 2>&1; do sleep 2; done
	make seed

rebuild:
	docker compose down
	docker compose up --build -d