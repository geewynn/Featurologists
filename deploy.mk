
# TODO: move this to GH secrets
GCP_PROJECT ?= indigo-union-312214
K8S_REGISTRY_PREFIX ?= gcr.io/$(GCP_PROJECT)

HELM_VERSION = v3.6.0
HELM_RELEASE = release
# HELM_COMMAND = tempate --debug
HELM_COMMAND = upgrade --atomic --wait --timeout=5m --install

# Create a Deploy Key and save it locally.
# see https://docs.github.com/en/developers/overview/managing-deploy-keys#deploy-keys
GIT_RSA_PATH ?=

GIT_REPO ?= $(shell git remote get-url origin)
GIT_REV ?= $(shell git rev-parse --short HEAD)

COMMON_IMAGE_TAG ?= $(GIT_REV)

JUPYTER_DEPLOY ?= true
JUPYTER_IMAGE_NAME ?= featurologists/jupyter
JUPYTER_IMAGE ?= $(JUPYTER_IMAGE_NAME):$(COMMON_IMAGE_TAG)

# K8S_NAMESPACE ?= featurologists-dev
K8S_NAMESPACE ?=
K8S_GIT_SECRET_NAME ?= git-secret


.PHONY: auth-docker
auth-docker:
	gcloud auth configure-docker


.PHONY: build-images
build-images:
	# build image: jupyter
	docker build -t $(JUPYTER_IMAGE) -f docker/jupyter.Dockerfile .


.PHONY: push-images
push-images: require-gcp-options
	# push image: jupyter
	docker tag $(JUPYTER_IMAGE) $(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE)
	docker push $(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE)


.PHONY: install-helm
install-helm:
	curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get | bash -s -- -v $(HELM_VERSION)


.PHONY: create-git-secret
create-git-secret: require-k8s-options require.K8S_GIT_SECRET_NAME require.GIT_RSA_PATH
	kubectl create ns $(K8S_NAMESPACE) |:
	kubectl -n $(K8S_NAMESPACE) create secret generic $(K8S_GIT_SECRET_NAME) \
		--from-file id_rsa="$(GIT_RSA_PATH)"


.PHONY: helm-deploy
helm-deploy: require-k8s-options
	helm -n $(K8S_NAMESPACE) $(HELM_COMMAND) $(HELM_RELEASE) ./deploy/featurologists \
		--set git.repo="$(GIT_REPO)" \
		--set git.revision="$(GIT_REV)" \
		--set git.deployKeySecret.name=$(K8S_GIT_SECRET_NAME) \
		--set jupyter.deploy="$(JUPYTER_DEPLOY)" \
		--set jupyter.image.repository="$(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE_NAME)" \
		--set jupyter.image.tag="$(COMMON_IMAGE_TAG)"

.PHONY: helm-test
helm-test: require-k8s-options
	helm -n $(K8S_NAMESPACE) test $(HELM_RELEASE)

.PHONY: helm-status
helm-status: require-k8s-options
	helm -n $(K8S_NAMESPACE) status $(HELM_RELEASE)

.PHONY: helm-history
helm-history: require-k8s-options
	helm -n $(K8S_NAMESPACE) history $(HELM_RELEASE)

.PHONY: helm-rollback
helm-rollback: require.GCP_PROJECT require.K8S_NAMESPACE
	helm -n $(K8S_NAMESPACE) rollback $(HELM_RELEASE) 0

.PHONY: helm-uninstall
helm-uninstall: require.GCP_PROJECT require.K8S_NAMESPACE
	helm -n $(K8S_NAMESPACE) uninstall $(HELM_RELEASE)


# --

require-gcp-options: require.GCP_PROJECT
require-k8s-options: require-gcp-options require.K8S_NAMESPACE

.SILENT: require.%
require.%:
	$(if $(value $(*)),,$(error Missing required argument $(*)))
