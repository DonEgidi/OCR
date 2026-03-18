.PHONY: help up down restart logs logs-api logs-ftp logs-frontend build rebuild test clean status health docs web

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Iniciar todos los servicios
	docker-compose up -d
	@echo "✓ Servicios iniciados"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API: http://localhost:8000"
	@echo "  Docs: http://localhost:8000/docs"

down: ## Detener todos los servicios
	docker-compose down
	@echo "✓ Servicios detenidos"

restart: ## Reiniciar todos los servicios
	docker-compose restart
	@echo "✓ Servicios reiniciados"

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-api: ## Ver logs solo de la API
	docker-compose logs -f ftp-api

logs-ftp: ## Ver logs solo del servidor FTP
	docker-compose logs -f ftp-server

logs-frontend: ## Ver logs solo del frontend
	docker-compose logs -f ftp-frontend

build: ## Construir las imágenes
	docker-compose build
	@echo "✓ Imágenes construidas"

rebuild: ## Reconstruir y reiniciar servicios
	docker-compose up -d --build
	@echo "✓ Servicios reconstruidos y reiniciados"

test: ## Ejecutar tests de la API
	@bash test_api.sh

clean: ## Limpiar contenedores, volúmenes e imágenes
	docker-compose down -v
	@echo "✓ Limpieza completa realizada"

status: ## Ver estado de los servicios
	@docker-compose ps

health: ## Verificar health de la API
	@curl -s http://localhost:8000/health | python3 -m json.tool || echo "Error: API no responde"

docs: ## Abrir documentación API en el navegador
	@echo "Abriendo documentación..."
	@xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || echo "Visita: http://localhost:8000/docs"

web: ## Abrir frontend en el navegador
	@echo "Abriendo frontend..."
	@xdg-open http://localhost:3000 2>/dev/null || open http://localhost:3000 2>/dev/null || echo "Visita: http://localhost:3000"

install: ## Instalar dependencias locales (para desarrollo)
	cd api && pip install -r requirements.txt
	cd frontend && npm install

dev: ## Modo desarrollo (sin Docker)
	cd api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Modo desarrollo frontend (sin Docker)
	cd frontend && npm run dev
