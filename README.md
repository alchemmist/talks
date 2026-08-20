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
