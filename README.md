Slide decks from all my public talks.

Private talks live in the `private` Git submodule and are stored in a separate
private repository. After cloning this repository, initialize them with
`git submodule update --init`.

Create a talk from the shared template:

```bash
make new-public
make new-private
```

Both commands prompt for a date in `DD-MM-YYYY` format and create the talk in
the appropriate repository.

To show a recording next to a talk on the public index, add an optional line to
the talk's `README.md`:

```md
Video: https://www.youtube.com/watch?v=example
```

The Russian `Видео:` label is supported as well.

Generate an SVG QR code with an optional icon in the center:

```bash
uv run scripts/generate_qr.py https://example.com qr.svg
uv run scripts/generate_qr.py https://example.com qr.svg --icon icon.svg
```

The icon mode uses high error correction and adds a white backing plate behind
the embedded SVG, PNG, JPEG, or WebP icon.
