all: spell lint

lint:
	markdownlint-cli2 . --fix

spell:
	-cspell-cli "**/*.{md,tex}"
