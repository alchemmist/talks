import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path


def read_date() -> str:
    while True:
        try:
            value = input("Talk date (DD-MM-YYYY): ").strip()
        except EOFError as error:
            raise SystemExit("Date is required") from error

        if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", value):
            print("Invalid format. Use DD-MM-YYYY, for example 20-08-2026.")
            continue

        try:
            datetime.strptime(value, "%d-%m-%Y")
        except ValueError:
            print("Invalid calendar date. Try again.")
            continue

        return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("visibility", choices=("public", "private"))
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    template = root / "template"
    destination_root = root if args.visibility == "public" else root / "private"

    if args.visibility == "private" and not (destination_root / ".git").exists():
        raise SystemExit("Private submodule is not initialized. Run: git submodule update --init")

    talk_date = read_date()
    destination = destination_root / talk_date

    if destination.exists():
        raise SystemExit(f"Talk already exists: {destination}")

    shutil.copytree(template, destination)

    for path in destination.rglob("*"):
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            path.write_text(content.replace("{{DATE}}", talk_date), encoding="utf-8")

    relative_destination = destination.relative_to(root)
    print(f"Created {args.visibility} talk: {relative_destination}")
    print(f"Next: cd {relative_destination} && pnpm install && pnpm dev")


if __name__ == "__main__":
    main()
