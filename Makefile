SHELL := /usr/bin/env bash

DATES := $(wildcard [0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9])
OUTDIR ?= build

PDFDIR := $(OUTDIR)/pdf
PAGESDIR := $(OUTDIR)/pages

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
			( cd $$d && yarn run slidev export slides.md --format pdf --output "../$(PDFDIR)/$$base.pdf" ); \
			outdir="../$(PAGESDIR)/$$base"; \
			mkdir -p $$outdir; \
			( cd $$d && yarn run slidev build slides.md --out $$outdir --base "/talks/$$base/" ); \
		fi \
	done

$(PDFDIR):
	mkdir -p $(PDFDIR)

$(PAGESDIR):
	mkdir -p $(PAGESDIR)

clean:
	rm -rf $(OUTDIR)
