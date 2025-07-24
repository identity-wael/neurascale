.PHONY: help setup test clean deploy

help:
	@echo "NeuraScale Neural Engine - Available commands:"
	@echo "  make setup    - Set up development environment"
	@echo "  make test     - Run all tests"
	@echo "  make clean    - Clean up generated files"
	@echo "  make lint     - Run code linters"
	@echo "  make format   - Format code with black"
	@echo "  make run      - Run local development server"

setup:
	./setup.sh

test:
	pytest tests/ -v --cov=. --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v -m "not performance"

lint:
	flake8 . --max-line-length=88 --extend-ignore=E203
	mypy . --ignore-missing-imports

format:
	black .
	isort .

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .mypy_cache

run-api:
	cd api && python app.py

run-emulators:
	@echo "Starting Google Cloud emulators..."
	gcloud beta emulators firestore start --host-port=localhost:8081 &
	gcloud beta emulators pubsub start --host-port=localhost:8085 &

docker-build:
	docker build -t neural-processor -f docker/Dockerfile.processor .
	docker build -t neural-api -f docker/Dockerfile.api .

docker-run:
	docker-compose -f docker-compose.dev.yml up
