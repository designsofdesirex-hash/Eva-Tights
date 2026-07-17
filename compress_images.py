from pathlib import Path
from PIL import Image, ImageOps
import io
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from skimage.metrics import structural_similarity as ssim

# ==========================================
# CONFIGURATION
# ==========================================

INPUT_DIR = Path("assets/img")
OUTPUT_DIR = Path("assets/webp")

PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# Mots-clés de fichiers qui doivent rester parfaitement nets (logos,
# schémas...) -> compression WebP sans aucune perte.
LOSSLESS_KEYWORDS = [
    "logo", "icon", "diagram", "schematic", "pcb",
    "layout", "drawing", "graph", "chart", "screenshot",
]

# Qualité perceptuelle cible pour les images "photo" (SSIM, 0-1).
# 0.985+ = différence invisible à l'œil nu dans l'immense majorité des cas.
# Baisser à 0.97-0.98 pour compresser encore plus si un léger risque
# de perte est acceptable.
TARGET_SSIM = 0.985

# Plage de qualité WebP explorée par la recherche dichotomique.
MIN_QUALITY = 60
MAX_QUALITY = 95

# Si le WebP obtenu est malgré tout plus gros que l'original (rare,
# photos déjà très compressées/bruitées), on garde l'original tel quel
# plutôt que d'agrandir le fichier.
KEEP_SMALLER_ORIGINAL = True

# Nombre de processus en parallèle (la recherche SSIM fait ~6 encodages
# par image, donc c'est nettement plus lent qu'une qualité fixe : on
# compense avec du parallélisme).
MAX_WORKERS = os.cpu_count() or 4

# ==========================================


def to_comparable_array(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB"), dtype=np.float32)


def encode_at_quality(img: Image.Image, quality: int) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=quality, method=6)
    return buf.getvalue()


def measure_ssim(reference_arr: np.ndarray, candidate_bytes: bytes) -> float:
    candidate_img = Image.open(io.BytesIO(candidate_bytes))
    candidate_arr = to_comparable_array(candidate_img)
    score, _ = ssim(
        reference_arr, candidate_arr,
        channel_axis=2, full=True, data_range=255,
    )
    return score


def find_best_quality(img: Image.Image):
    """Dichotomie : plus petite qualité WebP qui respecte TARGET_SSIM."""
    reference_arr = to_comparable_array(img)
    lo, hi = MIN_QUALITY, MAX_QUALITY

    # On vérifie d'abord le plafond : si même quality=MAX_QUALITY ne
    # suffit pas, c'est notre meilleure option possible (aucune perte
    # supplémentaire n'est acceptable, on ne descend pas plus bas).
    top_bytes = encode_at_quality(img, hi)
    top_score = measure_ssim(reference_arr, top_bytes)
    if top_score < TARGET_SSIM:
        return top_bytes, hi, top_score

    best_bytes, best_q, best_score = top_bytes, hi, top_score

    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode_at_quality(img, mid)
        score = measure_ssim(reference_arr, data)
        if score >= TARGET_SSIM:
            best_bytes, best_q, best_score = data, mid, score
            hi = mid - 1  # on tente encore plus petit
        else:
            lo = mid + 1  # pas assez fidèle, on remonte
    return best_bytes, best_q, best_score


def process_file(file: Path):
    relative = file.relative_to(INPUT_DIR)
    output_webp = OUTPUT_DIR / relative.with_suffix(".webp")
    output_fallback = OUTPUT_DIR / relative  # utilisé seulement si on garde l'original
    output_webp.parent.mkdir(parents=True, exist_ok=True)

    if output_webp.exists() or output_fallback.exists():
        return None  # déjà traité

    filename = file.name.lower()
    use_lossless = any(k in filename for k in LOSSLESS_KEYWORDS)

    try:
        with Image.open(file) as raw_img:
            # Sans ça, les photos prises en portrait avec un tag EXIF
            # d'orientation ressortent parfois tournées en WebP.
            img = ImageOps.exif_transpose(raw_img)

            if img.mode not in ("RGB", "RGBA"):
                has_alpha = "transparency" in img.info or img.mode in ("LA", "PA")
                img = img.convert("RGBA" if has_alpha else "RGB")

            if use_lossless:
                buf = io.BytesIO()
                img.save(buf, "WEBP", lossless=True, quality=100, method=6, exact=True)
                data, quality_used, score = buf.getvalue(), "lossless", 1.0
            else:
                data, quality_used, score = find_best_quality(img)

            original = file.stat().st_size

            if KEEP_SMALLER_ORIGINAL and len(data) >= original:
                output_fallback.write_bytes(file.read_bytes())
                new_size = original
                note = "original conservé (WebP plus lourd)"
            else:
                output_webp.write_bytes(data)
                new_size = len(data)
                note = f"q={quality_used} SSIM={score:.4f}"

        reduction = 100 * (1 - new_size / original) if original else 0
        return {
            "relative": str(relative), "original": original, "new": new_size,
            "reduction": reduction, "note": note, "error": None,
        }

    except Exception as e:
        return {"relative": str(relative), "error": str(e)}


def main():
    files = [f for f in INPUT_DIR.rglob("*") if f.suffix.lower() in PHOTO_EXTENSIONS]

    total_original = total_new = converted = kept_original = 0

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in files}
        for future in as_completed(futures):
            result = future.result()
            if result is None:
                continue
            if result["error"]:
                print(f"ERROR {futures[future]}")
                print(result["error"])
                continue

            total_original += result["original"]
            total_new += result["new"]
            converted += 1
            if "conservé" in result["note"]:
                kept_original += 1

            print(
                f"OK {result['relative']} | "
                f"{result['original']/1024:.1f} KB -> {result['new']/1024:.1f} KB "
                f"({result['reduction']:.1f}% smaller) | {result['note']}"
            )

    print("\n===================================")
    print(f"Converties        : {converted}")
    print(f"Original conservé : {kept_original}")
    print(f"Original          : {total_original/1024/1024:.2f} MB")
    print(f"Compressé         : {total_new/1024/1024:.2f} MB")
    if total_original:
        print(f"Gain              : {(1-total_new/total_original)*100:.1f}%")
    print("===================================")


if __name__ == "__main__":
    main()
