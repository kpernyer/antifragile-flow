# Marp slides build Makefile
# Requirements:
# - Node.js/npm (npx available)
# - Mermaid CLI for SVG generation
#
# Usage:
#   make        -> install dependencies and generate HTML
#   make html   -> slides/presentation.html
#   make diagrams -> generate SVG files from Mermaid diagrams
#   make watch  -> watch presentation.md and rebuild HTML
#   make serve  -> serve current directory with Marp server
#   make clean  -> remove slides/ and diagrams/

MD := presentation.md
OUTDIR := slides
DIAGRAMDIR := diagrams
MARPCLI := npx @marp-team/marp-cli
MERMAIDCLI := npx @mermaid-js/mermaid-cli

.PHONY: all html diagrams watch serve clean ensure_outdir ensure_diagramdir install

.DEFAULT_GOAL := all

all: install diagrams html

ensure_outdir:
	mkdir -p $(OUTDIR)

ensure_diagramdir:
	mkdir -p $(DIAGRAMDIR)

html: ensure_outdir
	$(MARPCLI) $(MD) -o $(OUTDIR)/presentation.html --allow-local-files

diagrams: ensure_diagramdir
	@echo "Creating diagram directory structure..."
	@echo "Note: SVG diagrams should be created manually or using external tools"
	@echo "Example: Use Mermaid Live Editor (https://mermaid.live/) to generate SVGs"
	@echo "Place generated SVG files in $(DIAGRAMDIR)/ directory"
	@echo "Diagrams directory ready: $(DIAGRAMDIR)/"

watch: ensure_outdir install
	$(MARPCLI) -w $(MD) -o $(OUTDIR)/presentation.html --allow-local-files

serve: install
	$(MARPCLI) -s . --open

clean:
	rm -rf $(OUTDIR)
	@echo "Note: $(DIAGRAMDIR)/ directory preserved"

install:
	npm install
