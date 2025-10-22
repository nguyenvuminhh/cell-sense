sinclude .env

# ----------- INSTALL -----------
.PHONY: install
install:
	poetry install

.PHONY: install_prod
install_prod:
	poetry install --no-d

# ----------- DOCKER -----------
.PHONY: docker_build
docker_build:
	docker build -t backend .

.PHONY: docker_run
docker_run:
	docker run -p 8000:8080 backend

# ----------- RUN -----------
.PHONY: run_dev
run_dev:
	poetry run uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload

.PHONY: run_prod
run_prod:
	make docker_build && make docker_run

.PHONY: ngrok_expose
ngrok_expose:
	ngrok http 8000

# ----------- GCLOUD -----------
.PHONY: setup_gcloud
setup_gcloud:
	gcloud config set account $(GCP_ACCOUNT_EMAIL) && \
	gcloud config set project $(GCP_PROJECT_ID) && \
	gcloud config set compute/region $(GCP_REGION) && \
	gcloud services enable run.googleapis.com artifactregistry.googleapis.com

.PHONY: gcloud_push_to_artifact_registry
gcloud_push_to_artifact_registry:
	docker tag backend europe-west1-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REGISTRY_REPO_NAME)/backend:latest && \
	docker push europe-west1-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REGISTRY_REPO_NAME)/backend:latest

.PHONY: gcloud_restart_cloud_run_service
gcloud_restart_cloud_run_service:
	gcloud run services update $(GCP_CLOUD_RUN_SERVICE_NAME) \
		--region europe-west1 \
		--no-traffic

.PHONY: gcloud_deploy_to_cloud_run
gcloud_deploy_to_cloud_run:
	make docker_build && \
	make gcloud_push_to_artifact_registry && \
	make gcloud_restart_cloud_run_service

.PHONY: gcloud_deploy_to_app_script
gcloud_deploy_to_app_script:
	cd app_script && clasp push
# ----------- PRE-COMMIT -----------
.PHONY: precommit
precommit:
	pre-commit run --all-files

.PHONY: test
test:
	echo "${GCP_ACCOUNT_EMAIL}"
