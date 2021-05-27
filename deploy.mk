K8S_REGISTRY_PREFIX = gcr.io/indigo-union-312214

JUPYTER_IMAGE_NAME = featurologists/jupyter
JUPYTER_IMAGE_TAG = 0.3
JUPYTER_IMAGE = $(JUPYTER_IMAGE_NAME):$(JUPYTER_IMAGE_TAG)

K8S_FEATUROLOGISTS_NS = featurologists
K8S_FEATUROLOGISTS_GIT_SECRET_NAME = git-secret
K8S_FEATUROLOGISTS_REVISION = dev


.PHONY: auth-docker
auth-docker:
	gcloud auth configure-docker


.PHONY: build-jupyter
build-jupyter:
	docker build -t $(JUPYTER_IMAGE) -f docker/jupyter.Dockerfile .

.PHONY: push-jupyter
push-jupyter:
	docker tag $(JUPYTER_IMAGE) $(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE)
	docker push $(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE)


HELM_CMD = install
# HELM_CMD = tempate --debug

# Create a Deploy Key and save it locally.
# see https://docs.github.com/en/developers/overview/managing-deploy-keys#deploy-keys
RSA_PATH ?=

.PHONY: create-git-secret
create-git-secret: require.RSA_PATH
	kubectl create ns $(K8S_FEATUROLOGISTS_NS) |:
	kubectl -n $(K8S_FEATUROLOGISTS_NS) create secret generic $(K8S_FEATUROLOGISTS_GIT_SECRET_NAME) \
		--from-file id_rsa="$(RSA_PATH)"

.PHONY: deploy-featurologists
deploy-featurologists:
	kubectl create ns $(K8S_FEATUROLOGISTS_NS) |:
	helm -n $(K8S_FEATUROLOGISTS_NS) $(HELM_CMD) $(K8S_FEATUROLOGISTS_REVISION) deploy/featurologists/ \
		--set git.repo="$(shell git remote get-url origin)" \
		--set git.deployKeySecret.name=$(K8S_FEATUROLOGISTS_GIT_SECRET_NAME) \
		--set jupyter.image.repository="$(K8S_REGISTRY_PREFIX)/$(JUPYTER_IMAGE_NAME)" \
		--set jupyter.image.tag="$(JUPYTER_IMAGE_TAG)"

.PHONY: uninstall-featurologists
uninstall-featurologists:
	helm -n $(K8S_FEATUROLOGISTS_NS) uninstall $(K8S_FEATUROLOGISTS_REVISION)


# --

.SILENT: require.%
require.%:
	$(if $(value $(*)),,$(error Missing required argument $(*)))
