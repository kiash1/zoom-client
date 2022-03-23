include .env

up:
	docker-compose up

build:
	git pull
	docker build -t . $(ZOOM_IMAGE) --no-cache

push: docker push $(ZOOM_IMAGE)

down: 
	docker-compose down

create-volume:
	docker volume create --name=db-zoom
