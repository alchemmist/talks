SHELL := /usr/bin/env bash

.PHONY: all lint spell build clean dev dev-theme restore-theme private-build private-lint private-spell new-public new-private

DATES := $(wildcard [0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9])
OUTDIR ?= build

PDFDIR := $(OUTDIR)/pdf
PAGESDIR := $(OUTDIR)/pages
THEME_DIR ?= ../slidev-theme-alchemmist
TALK ?= 27-08-2026

all: spell lint

lint:
	markdownlint-cli2 . --fix

spell:
	-cspell-cli "**/*.md"

build: $(PDFDIR) $(PAGESDIR)
	@for d in $(DATES); do \
		if [ -f $$d/slides.md ]; then \
			echo "Building $$d..."; \
			base=$$(basename $$d); \
			( cd $$d && pnpm exec slidev export slides.md --format pdf --output "../$(PDFDIR)/$$base.pdf" ); \
			outdir="../$(PAGESDIR)/$$base"; \
			mkdir -p $$outdir; \
			( cd $$d && pnpm exec slidev build slides.md --out $$outdir --base "/talks/$$base/" ); \
		fi \
	done

$(PDFDIR):
	mkdir -p $(PDFDIR)

$(PAGESDIR):
	mkdir -p $(PAGESDIR)

clean:
	rm -rf $(OUTDIR)

dev dev-theme:
	@test -f "$(TALK)/slides.md" || (echo "Talk not found: $(TALK)" && exit 1)
	@test -f "$(THEME_DIR)/package.json" || (echo "Theme not found: $(THEME_DIR)" && exit 1)
	cd "$(TALK)" && pnpm install --frozen-lockfile
	rm -f "$(TALK)/node_modules/slidev-theme-alchemmist"
	ln -s "$(abspath $(THEME_DIR))" "$(TALK)/node_modules/slidev-theme-alchemmist"
	cd "$(TALK)" && pnpm dev

restore-theme:
	@test -f "$(TALK)/slides.md" || (echo "Talk not found: $(TALK)" && exit 1)
	cd "$(TALK)" && pnpm install --force --frozen-lockfile

private-build:
	$(MAKE) -C private build

private-lint:
	$(MAKE) -C private lint

private-spell:
	$(MAKE) -C private spell

new-public:
	python3 scripts/new_talk.py public

new-private:
	python3 scripts/new_talk.py private
