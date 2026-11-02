HUGO := hugo
HUGO_ENV := GOWORK=off HUGO_MODULE_WORKSPACE=off
HUGO_DEV_FLAGS := -D --bind 0.0.0.0 --port 1313 --disableFastRender
HUGO_BUILD_FLAGS := --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings

default: dev

dev:
	$(HUGO_ENV) $(HUGO) server $(HUGO_DEV_FLAGS)

serve: dev

build:
	$(HUGO_ENV) $(HUGO) build $(HUGO_BUILD_FLAGS)

check:
	$(HUGO_ENV) go mod verify
	$(HUGO_ENV) $(HUGO) build $(HUGO_BUILD_FLAGS)
	python3 bin/check_internal_links.py public

.PHONY: default dev serve build check
