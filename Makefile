up:
	docker compose -f docker.local.yaml up -d
down:
	docker compose -f docker.local.yaml down && docker network prune --force