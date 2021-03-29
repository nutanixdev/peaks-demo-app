# Project Variables
REPO_NAME ?= devops
VERSION ?= 0.1.$(BUILD_ID)

ORG_NAME := $(REPO_NAME)

# Docker Compose Files
DEV_COMPOSE_FILE := docker/dev/docker-compose.yml
REL_COMPOSE_FILE := docker/release/docker-compose.yml

# Docker Compose Project Names
REL_PROJECT := $(REPO_NAME)$(BUILD_ID)
DEV_PROJECT := $(REL_PROJECT)dev

DB_SERVICE_NAME := mongodb
APP_SERVICE_NAME := nodejs
WEB_SERVICE_NAME := nginx

# Check and Inspect Logic
INSPECT := $$(docker-compose -p $$1 -f $$2 ps -q $$3 | xargs -I ARGS docker inspect -f "{{ .State.ExitCode }}" ARGS)
CHECK := @bash -c '\
	if [[ $(INSPECT) -ne 0 ]]; \
		then exit $(INSPECT); fi' VALUE

# Docker registry
DOCKER_REGISTRY ?= 

# Artifactory instance
ARTIFACTORY_INSTANCE ?= 

# Tags
TAGS := latest $(VERSION)

.PHONY: test build release clean tag buildtag login logout publish deploy

test:
	$(info "Creating cache volume...")
	@ docker volume create --name cache
	$(info "Pulling latest images...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) pull
	$(info "Building images...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) build --pull test
	$(info "Ensuring database is ready...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) run --rm agent
	$(info "Running tests...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) up test
	${CHECK} $(DEV_PROJECT) $(DEV_COMPOSE_FILE) test
	$(info "Testing complete")

build:
	$(info "Pull Calm DSL image...")
	@ docker pull ntnx/calm-dsl
	$(info "Start Calm DSL container...")
	@ docker run -d -t --env-file ~/calm/$(BLUEPRINT_NAME)_env.cfg -v ~/calm/config:/root/.calm -v $(shell pwd)/dsl:/root/dsl --name calm-dsl-$(REPO_NAME) ntnx/calm-dsl
	$(info "Update Calm DSL cache...")
	@ docker exec calm-dsl-$(REPO_NAME) calm update cache
	$(info "Create Calm DSL blueprint...")
	@ docker exec calm-dsl-$(REPO_NAME) calm create bp -f /root/dsl/$(BLUEPRINT_NAME)/blueprint.py --name "$(BLUEPRINT_NAME)" -fc
	$(info "Creating builder image...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) build builder
	$(info "Building application artifacts...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) up builder
	${CHECK} $(DEV_PROJECT) $(DEV_COMPOSE_FILE) builder
	$(info "Copying application artifacts...")
	@ docker cp $$(docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) ps -q builder):/output/nodejs-app.tar.gz target
	@ curl -u$$ARTIFACTORY_USER:$$ARTIFACTORY_PASSWORD -T target/nodejs-app.tar.gz "http://$(ARTIFACTORY_INSTANCE):8081/artifactory/$(REPO_NAME)-local-repo/$(REL_PROJECT)/nodejs-app.tar.gz"
	$(info "Copying web artifacts...")
	@ tar -C web/src/ -cvzf target/web.tar.gz .
	@ curl -u$$ARTIFACTORY_USER:$$ARTIFACTORY_PASSWORD -T target/web.tar.gz "http://$(ARTIFACTORY_INSTANCE):8081/artifactory/$(REPO_NAME)-local-repo/$(REL_PROJECT)/web.tar.gz"
	$(info "Copying db artifacts...")
	@ tar -C db/mongo/data/ -cvzf target/db.tar.gz .
	@ curl -u$$ARTIFACTORY_USER:$$ARTIFACTORY_PASSWORD -T target/db.tar.gz "http://$(ARTIFACTORY_INSTANCE):8081/artifactory/$(REPO_NAME)-local-repo/$(REL_PROJECT)/db.tar.gz"
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) down -v
	$(info "Build complete")

release:
	$(info "Pulling latest images...")
	@ docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) build nginx
	@ docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) run --rm agent
	@ docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) run -d nginx
	$(info "Acceptance testing complete")

clean:
	$(info "Destroying development environment...")
	@ docker-compose -p $(DEV_PROJECT) -f $(DEV_COMPOSE_FILE) down -v
	@ docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) down -v
	$(info "Removing dangling images...")
	@ docker images -q -f dangling=true -f label=application=$(REPO_NAME) | xargs -I ARGS docker rmi -f ARGS
	@ docker kill calm-dsl-$(REPO_NAME)
	@ docker rm calm-dsl-$(REPO_NAME)
	$(info "Clean complete")

tag: 
	$(info "Tagging release image with tags...")
	$(info "Tagging $(DB_IMAGE_ID) image with tags...")
	@ $(foreach tag,$(TAGS), docker tag $(DB_IMAGE_ID) $(DOCKER_REGISTRY)/$(ORG_NAME)/$(DB_SERVICE_NAME):$(tag);)
	$(info "Tagging $(APP_IMAGE_ID) image with tags...")
	@ $(foreach tag,$(TAGS), docker tag $(APP_IMAGE_ID) $(DOCKER_REGISTRY)/$(ORG_NAME)/$(APP_SERVICE_NAME):$(tag);)
	$(info "Tagging $(WEB_IMAGE_ID) image with tags...")
	@ $(foreach tag,$(TAGS), docker tag $(WEB_IMAGE_ID) $(DOCKER_REGISTRY)/$(ORG_NAME)/$(WEB_SERVICE_NAME):$(tag);)
	$(info "Tagging complete")

login:
	$(info "Logging in to Docker registry $(DOCKER_REGISTRY)...")
	@ docker login -u $$DOCKER_REGISTRY_USER -p $$DOCKER_REGISTRY_PASSWORD $(DOCKER_REGISTRY)
	$(info "Logged in to Docker registry $(DOCKER_REGISTRY)")
	$(info "Logging in to Docker Hub ...")
	@ docker login -u $$DOCKER_HUB_USER -p $$DOCKER_HUB_PASSWORD
	$(info "Logged in to Docker Hub")

logout:
	$(info "Logging out of Docker registry $(DOCKER_REGISTRY)...")
	@ docker logout $(DOCKER_REGISTRY)
	$(info "Logged out of Docker registry $(DOCKER_REGISTRY)")
	$(info "Logging out of Docker Hub...")
	@ docker logout
	$(info "Logged out of Docker Hub")

publish:
	$(info "Publishing release image $(DB_IMAGE_ID) to $(DOCKER_REGISTRY)/$(ORG_NAME)/$(DB_SERVICE_NAME)...")
	@ $(foreach tag,$(shell echo $(DB_REPO_EXPR)), docker push $(tag);)
	$(info "Publishing release image $(APP_IMAGE_ID) to $(DOCKER_REGISTRY)/$(ORG_NAME)/$(APP_SERVICE_NAME)...")
	@ $(foreach tag,$(shell echo $(APP_REPO_EXPR)), docker push $(tag);)
	$(info "Publishing release image $(WEB_IMAGE_ID) to $(DOCKER_REGISTRY)/$(ORG_NAME)/$(WEB_SERVICE_NAME)...")
	@ $(foreach tag,$(shell echo $(WEB_REPO_EXPR)), docker push $(tag);)
	$(info "Publish complete")

# Get container id of application service container
DB_CONTAINER_ID := $$(docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) ps -q $(DB_SERVICE_NAME))
APP_CONTAINER_ID := $$(docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) ps -q $(APP_SERVICE_NAME))
WEB_CONTAINER_ID := $$(docker-compose -p $(REL_PROJECT) -f $(REL_COMPOSE_FILE) ps -q $(WEB_SERVICE_NAME))

# Get image id of application service
DB_IMAGE_ID := $$(docker inspect -f '{{ .Image }}' $(DB_CONTAINER_ID))
APP_IMAGE_ID := $$(docker inspect -f '{{ .Image }}' $(APP_CONTAINER_ID))
WEB_IMAGE_ID := $$(docker inspect -f '{{ .Image }}' $(WEB_CONTAINER_ID))

# REPO FILTER
DB_REPO_FILTER := $(DOCKER_REGISTRY)/$(ORG_NAME)/$(DB_SERVICE_NAME)[^[:space:]|\$$]*
APP_REPO_FILTER := $(DOCKER_REGISTRY)/$(ORG_NAME)/$(APP_SERVICE_NAME)[^[:space:]|\$$]*
WEB_REPO_FILTER := $(DOCKER_REGISTRY)/$(ORG_NAME)/$(WEB_SERVICE_NAME)[^[:space:]|\$$]*

# Introspect repository tags
DB_REPO_EXPR := $$(docker inspect -f '{{range .RepoTags}}{{.}} {{end}}' $(DB_IMAGE_ID) | grep -oh "$(DB_REPO_FILTER)" | xargs)
APP_REPO_EXPR := $$(docker inspect -f '{{range .RepoTags}}{{.}} {{end}}' $(APP_IMAGE_ID) | grep -oh "$(APP_REPO_FILTER)" | xargs)
WEB_REPO_EXPR := $$(docker inspect -f '{{range .RepoTags}}{{.}} {{end}}' $(WEB_IMAGE_ID) | grep -oh "$(WEB_REPO_FILTER)" | xargs)

