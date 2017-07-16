SHELL = /bin/bash
GIT_BRANCH := $(shell git branch | sed -n -e 's/^\* \(.*\)/\1/p')
IMAGE_NAME ?= 847754352879.dkr.ecr.eu-west-1.amazonaws.com/consul-zone-sync
IMAGE_VERSION ?= $(shell docker/tag_helper.sh)
SOURCE_BUNDLE_ARCHIVE_NAME = dubizzle-uae-$(IMAGE_VERSION).zip
REFRESH_CODE ?= 'yes'

docker: docker_build docker_push docker_clean

docker_build:
ifeq ($(REFRESH_CODE), 'yes')
	git archive --format tar.gz --output docker/archive.tar.gz $(GIT_BRANCH)
endif
	docker build -t $(IMAGE_NAME):$(GIT_BRANCH) -f docker/Dockerfile .

docker_push:
	docker push $(IMAGE_NAME):$(GIT_BRANCH)

docker_clean:
	-rm docker/archive.tar.gz
