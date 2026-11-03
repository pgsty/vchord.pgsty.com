HUGO := hugo
HUGO_ENV := GOWORK=off HUGO_MODULE_WORKSPACE=off
HUGO_DEV_FLAGS := -D --bind 0.0.0.0 --port 1313 --disableFastRender --noBuildLock
HUGO_BUILD_FLAGS := --noBuildLock --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings

default: dev

dev:
	$(HUGO_ENV) $(HUGO) server $(HUGO_DEV_FLAGS)

serve: dev

build:
	$(HUGO_ENV) $(HUGO) build $(HUGO_BUILD_FLAGS)

sync-download:
	python3 bin/sync_download.py

check:
	$(HUGO_ENV) go mod verify
	$(HUGO_ENV) $(HUGO) build $(HUGO_BUILD_FLAGS) -d /tmp/vchord-check-public
	python3 bin/check_internal_links.py /tmp/vchord-check-public
	rm -rf /tmp/vchord-check-public resources .hugo_build.lock

.PHONY: default dev serve build sync-download check
