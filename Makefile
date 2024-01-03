start:
	docker-compose build
	docker-compose start db
	make init
	docker-compose up

init:
	docker-compose run web scripts/init.sh

migrations:
	docker-compose run web scripts/migrations.sh

migrate:
	docker-compose run web scripts/migrate.sh

test:
	docker-compose run web scripts/test.sh