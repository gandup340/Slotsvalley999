"""Crop SlotsValley brand asset and write favicon/logo PNGs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

SRC = Path(
    r"C:\Users\nepsa\.cursor\projects\c-Users-nepsa-Downloads-Slotsvalley999\assets"
    r"\c__Users_nepsa_AppData_Roaming_Cursor_User_workspaceStorage_45abd4f016e9e9f55351f961a981ff74"
    r"_images_5866bee5-2a61-451a-8262-b798eaa982fe-3a97dde7-f3b1-4840-9692-82b6abcb1506.jpg"
)
OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"


def is_checkerboard(r: int, g: int, b: int) -> bool:
    # Light checkerboard / near-white canvas around the icon
    if r > 210 and g > 210 and b > 210:
        return True
    if abs(r - g) < 18 and abs(g - b) < 18 and r > 155:
        return True
    return False


def content_bbox(im: Image.Image, y_max: int | None = None) -> tuple[int, int, int, int]:
    pixels = im.load()
    w, h = im.size
    ymax = h if y_max is None else min(h, y_max)
    xs: list[int] = []
    ys: list[int] = []
    for y in range(ymax):
        for x in range(w):
            r, g, b, _a = pixels[x, y]
            if is_checkerboard(r, g, b):
                continue
            xs.append(x)
            ys.append(y)
    if not xs:
        raise SystemExit("No icon content found")
    return min(xs), min(ys), max(xs), max(ys)


def make_square(im: Image.Image, pad: int = 8) -> Image.Image:
    # Transparent square canvas with icon centered
    w, h = im.size
    side = max(w, h) + pad * 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return canvas


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = Image.open(SRC).convert("RGBA")
    print("source", raw.size)

    # Drop caption strip at bottom (~12%)
    cut = int(raw.height * 0.88)
    left, top, right, bottom = content_bbox(raw, y_max=cut)
    # Small padding inside the crop so rounded corners aren't clipped
    pad = max(4, (right - left) // 80)
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(raw.width - 1, right + pad)
    bottom = min(cut - 1, bottom + pad)
    icon = raw.crop((left, top, right + 1, bottom + 1))
    print("cropped", icon.size, "bbox", (left, top, right, bottom))

    # Replace residual light checkerboard with transparency
    pixels = icon.load()
    for y in range(icon.height):
        for x in range(icon.width):
            r, g, b, a = pixels[x, y]
            if is_checkerboard(r, g, b):
                pixels[x, y] = (0, 0, 0, 0)

    square = make_square(icon, pad=0)

    targets = {
        "icon-512.png": 512,
        "icon-192.png": 192,
        "apple-touch-icon.png": 180,
        "favicon-32.png": 32,
        "favicon-16.png": 16,
    }
    for name, size in targets.items():
        out = square.resize((size, size), Image.Resampling.LANCZOS)
        path = OUT_DIR / name
        out.save(path, format="PNG", optimize=True)
        print("wrote", path)

    # Multi-size favicon.ico
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    ico_images = [square.resize(s, Image.Resampling.LANCZOS) for s in ico_sizes]
    ico_path = OUT_DIR / "favicon.ico"
    ico_images[0].save(
        ico_path,
        format="ICO",
        sizes=ico_sizes,
        append_images=ico_images[1:],
    )
    print("wrote", ico_path)

    # Also keep a clean logo copy for reference
    logo_path = OUT_DIR / "logo.png"
    square.resize((512, 512), Image.Resampling.LANCZOS).save(logo_path, format="PNG", optimize=True)
    print("wrote", logo_path)


if __name__ == "__main__":
    main()
