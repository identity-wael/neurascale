.PHONY: help setup test clean deploy

help:
	@echo "NeuraScale Neural Engine - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make setup         - Set up development environment"
	@echo "  make test          - Run all tests"
	@echo "  make clean         - Clean up generated files"
	@echo "  make lint          - Run code linters"
	@echo "  make format        - Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build all Docker images"
	@echo "  make docker-push   - Push images to GCR"
	@echo "  make docker-run    - Run services with Docker Compose"
	@echo "  make docker-stop   - Stop Docker Compose services"
	@echo "  make docker-logs   - View Docker Compose logs"
	@echo ""
	@echo "Kubernetes:"
	@echo "  make k8s-validate  - Validate Docker-K8s alignment"
	@echo "  make k8s-deploy    - Deploy to Kubernetes"
	@echo "  make k8s-status    - Check deployment status"
	@echo "  make k8s-logs      - View Kubernetes logs"
	@echo "  make k8s-delete    - Delete Kubernetes deployment"

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

# Docker commands
docker-build:
	@echo "Building all Docker images..."
	docker-compose -f docker/compose/docker-compose.yml -f docker/compose/docker-compose.k8s.yml build

docker-build-%:
	@echo "Building $* image..."
	docker build -t gcr.io/development-neurascale/$*:latest -f docker/dockerfiles/services/$*/Dockerfile ..

docker-push:
	@echo "Pushing images to GCR..."
	docker-compose -f docker/compose/docker-compose.yml -f docker/compose/docker-compose.k8s.yml push

docker-run:
	docker-compose -f docker/compose/docker-compose.yml up -d

docker-stop:
	docker-compose -f docker/compose/docker-compose.yml down

docker-logs:
	docker-compose -f docker/compose/docker-compose.yml logs -f

# Kubernetes commands
k8s-validate:
	./scripts/validate-k8s-docker.sh

k8s-deploy:
	helm upgrade --install neural-engine ./kubernetes/helm/neural-engine \
		--namespace neural-engine --create-namespace

k8s-deploy-dev:
	helm upgrade --install neural-engine ./kubernetes/helm/neural-engine \
		-f ./kubernetes/helm/neural-engine/values-dev.yaml \
		--namespace neural-engine-dev --create-namespace

k8s-status:
	kubectl get pods,svc,ing -n neural-engine

k8s-logs:
	kubectl logs -n neural-engine -l app.kubernetes.io/name=neural-engine --tail=100 -f

k8s-delete:
	helm uninstall neural-engine -n neural-engine
