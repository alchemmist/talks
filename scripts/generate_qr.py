# /// script
# requires-python = ">=3.11"
# dependencies = ["qrcode>=8.2"]
# ///

import argparse
import base64
import io
import mimetypes
import xml.etree.ElementTree as ET
from pathlib import Path

import qrcode
import qrcode.image.svg

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
ERROR_CORRECTION = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("data")
    parser.add_argument("output", type=Path)
    parser.add_argument("--icon", type=Path)
    parser.add_argument("--icon-scale", type=float, default=0.16)
    parser.add_argument("--border", type=int, default=2)
    parser.add_argument("--error-correction", choices=ERROR_CORRECTION)
    return parser.parse_args()


def image_data_url(path: Path) -> str:
    mime_type = mimetypes.guess_type(path.name)[0]
    if mime_type not in {"image/svg+xml", "image/png", "image/jpeg", "image/webp"}:
        raise ValueError(f"unsupported icon format: {path.suffix}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def add_icon(svg: bytes, icon: Path, scale: float) -> bytes:
    if not 0 < scale <= 0.25:
        raise ValueError("--icon-scale must be greater than 0 and at most 0.25")

    ET.register_namespace("", SVG_NAMESPACE)
    root = ET.fromstring(svg)
    view_box = [float(value) for value in root.attrib["viewBox"].split()]
    _, _, width, height = view_box
    icon_size = min(width, height) * scale
    background_size = icon_size * 1.4
    center_x = width / 2
    center_y = height / 2

    background = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}rect",
        {
            "x": str(center_x - background_size / 2),
            "y": str(center_y - background_size / 2),
            "width": str(background_size),
            "height": str(background_size),
            "rx": str(background_size * 0.18),
            "fill": "#fff",
        },
    )
    background.tail = ""
    icon_element = ET.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}image",
        {
            "x": str(center_x - icon_size / 2),
            "y": str(center_y - icon_size / 2),
            "width": str(icon_size),
            "height": str(icon_size),
            "preserveAspectRatio": "xMidYMid meet",
            "href": image_data_url(icon),
        },
    )
    icon_element.tail = ""
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def generate(args: argparse.Namespace) -> None:
    if args.output.suffix.lower() != ".svg":
        raise ValueError("output must use the .svg extension")
    if args.border < 0:
        raise ValueError("--border must not be negative")
    if args.icon and not args.icon.is_file():
        raise FileNotFoundError(args.icon)

    correction = args.error_correction or ("H" if args.icon else "M")
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECTION[correction],
        box_size=10,
        border=args.border,
    )
    qr.add_data(args.data)
    qr.make(fit=True)

    buffer = io.BytesIO()
    image = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    image.save(buffer)
    svg = buffer.getvalue()
    if args.icon:
        svg = add_icon(svg, args.icon, args.icon_scale)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(svg)


def main() -> None:
    generate(parse_args())


if __name__ == "__main__":
    main()
