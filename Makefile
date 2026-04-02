# ---- Docker ----
up:
	docker-compose -f conf/docker-compose.yml up -d

down:
	docker-compose -f conf/docker-compose.yml down

build:
	docker-compose -f conf/docker-compose.yml build

logs:
	docker-compose -f conf/docker-compose.yml logs -f

# ---- Local Development ----
bot_local:
	python bot/main.py

migrate_local:
	python manage.py migrate

makemigrations_local:
	python manage.py makemigrations

shell:
	python manage.py shell

runserver:
	python manage.py runserver

# ---- Testing ----
test:
	pytest --cov=core --cov-report=term-missing

lint:
	ruff check .
