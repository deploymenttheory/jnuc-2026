# Local Mac build for the deck downloads.
#
# The downloads cannot be built in CI: GitHub's runners have no Keynote, and a
# Linux capture would render the decks in substitute fonts. So they are built
# here, by hand, and committed. Rebuild and commit them in the same change as
# any deck edit.
#
#   make pptx        PowerPoint only - works on any Mac, no Keynote needed
#   make key         Keynote only    - needs Keynote installed
#   make downloads   both, from ONE capture pass, so the two formats match
#
# Each target installs what it needs first, so a clean checkout only needs
# `make pptx`. Everything underneath is `tools/build-downloads.mjs`; the npm
# scripts still work if you prefer them.

SHELL := /bin/bash

# npm ci wipes node_modules, which takes the stamp with it, so a reinstall
# re-checks the browser too. `playwright install` is a no-op when the browser
# is already in ~/Library/Caches/ms-playwright.
DEPS_STAMP := node_modules/.package-lock.json
CHROMIUM_STAMP := node_modules/.chromium-installed

.DEFAULT_GOAL := help
.PHONY: help pptx key downloads clean-downloads

help: ## Show this help
	@echo "Deck downloads (run on a Mac):"
	@echo
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[1m%-16s\033[0m %s\n", $$1, $$2}'
	@echo
	@echo "Output lands next to each deck under presentations/ and IS committed."

## --- builds -----------------------------------------------------------------

pptx: mac $(CHROMIUM_STAMP) ## Build the PowerPoint downloads (no Keynote required)
	npm run build:pptx

key: mac $(CHROMIUM_STAMP) ## Build the Keynote downloads (needs Keynote)
	@test -d /Applications/Keynote.app \
		|| { echo "Keynote is not installed - 'make pptx' builds the PowerPoint half without it."; exit 1; }
	npm run build:key

downloads: mac $(CHROMIUM_STAMP) ## Build both formats from one capture pass (needs Keynote)
	@test -d /Applications/Keynote.app \
		|| { echo "Keynote is not installed - 'make pptx' builds the PowerPoint half without it."; exit 1; }
	npm run build

## --- setup ------------------------------------------------------------------

$(DEPS_STAMP): package.json package-lock.json
	@# If this fails with EACCES on ~/.npm, the cache is owned by root:
	@#   sudo chown -R $$(id -u):$$(id -g) ~/.npm
	npm ci

$(CHROMIUM_STAMP): $(DEPS_STAMP)
	npx playwright install chromium
	@touch $@

## --- housekeeping -----------------------------------------------------------

# Deliberately not called `clean`: these files are committed, so removing them
# is a decision, not tidying up. Only useful to prove a build really reran.
clean-downloads: ## Delete the built .key and .pptx downloads (they are committed - use with care)
	rm -rf presentations/*/*.key presentations/*/*.pptx

# Mac-only even for the PowerPoint half: the capture has to happen on a machine
# with the decks' fonts, or the slides come out in substitutes.
.PHONY: mac
mac:
	@test "$$(uname -s)" = "Darwin" \
		|| { echo "The deck downloads can only be built on a Mac."; exit 1; }
