from pathlib import Path
from PIL import Image
import os

# ==========================================
# CONFIGURATION
# ==========================================

INPUT_DIR = Path("assets/img")      # Source folder
OUTPUT_DIR = Path("assets/webp")       # Destination folder

PHOTO_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff"
}

# File keywords that should stay perfectly sharp
LOSSLESS_KEYWORDS = [
    "logo",
    "icon",
    "diagram",
    "schematic",
    "pcb",
    "layout",
    "drawing",
    "graph",
    "chart",
    "screenshot"
]

# ==========================================

total_original = 0
total_new = 0
converted = 0

for file in INPUT_DIR.rglob("*"):

    if file.suffix.lower() not in PHOTO_EXTENSIONS:
        continue

    relative = file.relative_to(INPUT_DIR)
    output = OUTPUT_DIR / relative.with_suffix(".webp")
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.exists():
        continue

    filename = file.name.lower()

    use_lossless = any(k in filename for k in LOSSLESS_KEYWORDS)

    try:
        with Image.open(file) as img:
            # Pillow uses quality=100 and lossless=True for lossless webp
            # For lossy, we use quality=90
            
            # Ensure image is in RGB mode for WebP conversion if it's not RGBA
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if img.mode == "P" and "transparency" in img.info else "RGB")

            img.save(
                output,
                "WEBP",
                lossless=use_lossless,
                quality=100 if use_lossless else 90,
                method=6
            )
            
        original = file.stat().st_size
        new = output.stat().st_size

        total_original += original
        total_new += new
        converted += 1

        reduction = 100 * (1 - new / original)

        print(
            f"OK {relative} | "
            f"{original/1024:.1f} KB → "
            f"{new/1024:.1f} KB "
            f"({reduction:.1f}% smaller)"
        )

    except Exception as e:
        print(f"ERROR {file}")
        print(e)
        continue

print("\n===================================")
print(f"Converted : {converted}")
print(f"Original  : {total_original/1024/1024:.2f} MB")
print(f"WebP      : {total_new/1024/1024:.2f} MB")

if total_original:
    print(f"Saved     : {(1-total_new/total_original)*100:.1f}%")
print("===================================")
