import os
import random
import json
import glob
import re

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WEBP_DIR = os.path.join("assets", "webp")
VID_DIR = os.path.join("assets", "Vid_optimized")

BRAND = "eva-tights"

# Mot-clé de marque + variantes qu'on veut voir apparaître régulièrement
# (mais pas sur 100% des fichiers, sinon ça sonne répétitif / spam).
BRAND_VARIANTS = [
    "eva-tights",
    "eva-tights-dominatrice-francaise",
]

# Pools de mots-clés par catégorie. On choisit 2-3 mots-clés issus d'UNE
# catégorie principale (+ parfois 1 mot d'une catégorie secondaire), pas un
# mélange aléatoire de partout.
CATEGORY_KEYWORDS = {
    "feet": [
        "feet-fetish", "foot-fetish", "pieds", "modele-pieds-francaise",
        "arches", "soles", "plantes-de-pieds", "orteils",
    ],
    "nylon": [
        "nylon", "collants", "bas-nylon", "stockings", "pantyhose", "voile",
    ],
    "heels_legs": [
        "heels", "talons", "talons-aiguilles", "legs", "jambes", "escarpins",
    ],
    "domination": [
        "domina", "femdom", "dominatrice", "domination", "maitresse",
        "domina-de-luxe",
    ],
    "bdsm_submission": [
        "bdsm", "soumis", "soumission", "esclave", "fetish", "domination-stricte",
    ],
    "findom": [
        # Thème dédié : à réserver à une petite partie des images
        # (contenu findom/tribut), pas à toute la galerie.
        "findom", "paypig", "tribut", "financial-domination", "cocu", "cuckold",
    ],
    "luxury": [
        "luxury", "editorial-luxe", "contenu-exclusif", "premium-content",
        "vente-photos-pieds",
    ],
}

# Répartition thématique : combien d'images (en proportion) reçoivent
# chaque thème principal. Ajuste selon la répartition réelle de ta galerie.
THEME_WEIGHTS = {
    "feet": 0.30,
    "nylon": 0.20,
    "heels_legs": 0.15,
    "domination": 0.15,
    "bdsm_submission": 0.10,
    "findom": 0.05,
    "luxury": 0.05,
}

# Mappe un nom de fichier ACTUEL à une catégorie forcée, si tu sais ce que
# montre l'image. Exemple : {"IMG_00231.webp": "findom"}
# Laisse vide pour un tirage pondéré (THEME_WEIGHTS) sur toutes les images.
CATEGORY_MAP = {}

def get_files_to_rename():
    files = []
    if os.path.exists(WEBP_DIR):
        for f in os.listdir(WEBP_DIR):
            if f.endswith(".webp"):
                files.append((WEBP_DIR, f))
    if os.path.exists(VID_DIR):
        for f in os.listdir(VID_DIR):
            if f.endswith(".mp4"):
                files.append((VID_DIR, f))
    return files

def pick_theme(old_name):
    if old_name in CATEGORY_MAP:
        return CATEGORY_MAP[old_name]
    themes, weights = zip(*THEME_WEIGHTS.items())
    return random.choices(themes, weights=weights, k=1)[0]

def generate_new_name(ext, index, old_name, is_portrait=False):
    if is_portrait:
        return f"{BRAND}-dominatrice-francaise-portrait{ext}"

    theme = pick_theme(old_name)
    primary_pool = CATEGORY_KEYWORDS[theme]
    primary_kws = random.sample(primary_pool, min(2, len(primary_pool)))

    # Un mot-clé secondaire pioché dans une autre catégorie, pour varier
    # sans perdre la cohérence thématique principale.
    other_categories = [c for c in CATEGORY_KEYWORDS if c != theme]
    secondary_cat = random.choice(other_categories)
    secondary_kw = random.choice(CATEGORY_KEYWORDS[secondary_cat])

    brand = random.choice(BRAND_VARIANTS) if random.random() < 0.15 else BRAND
    kw_str = "-".join(primary_kws + [secondary_kw])
    return f"{brand}-{kw_str}-{index:02d}{ext}"

def generate_alt_text(theme, index):
    """Texte alt/légende FR + EN, plus riche que le nom de fichier :
    c'est ce texte que les moteurs génératifs et Google Images utilisent
    pour comprendre et citer le contenu."""
    templates_fr = {
        "feet": "Eva Tights, dominatrice française, met en scène ses pieds dans une séance éditoriale de luxe (foot fetish, arches).",
        "nylon": "Eva Tights en collants nylon fins, esthétique éditoriale haut de gamme (nylon fetish, bas).",
        "heels_legs": "Eva Tights met en valeur jambes et talons aiguilles dans une composition éditoriale luxe.",
        "domination": "Eva Tights, domina française, pose dans une scène de domination éditoriale (femdom, dominatrice de luxe).",
        "bdsm_submission": "Eva Tights, dominatrice BDSM française, dans une mise en scène de soumission et domination stricte.",
        "findom": "Contenu findom / tribut par Eva Tights, dominatrice française spécialisée en domination financière (paypig).",
        "luxury": "Contenu éditorial de luxe par Eva Tights, dominatrice et modèle de pieds française.",
    }
    templates_en = {
        "feet": "Eva Tights, French dominatrix, showcases her feet in a luxury editorial session (foot fetish, arches).",
        "nylon": "Eva Tights in fine nylon stockings, high-end editorial aesthetic (nylon fetish).",
        "heels_legs": "Eva Tights highlights legs and stiletto heels in a luxury editorial composition.",
        "domination": "Eva Tights, French domina, poses in a femdom editorial scene (luxury dominatrix).",
        "bdsm_submission": "Eva Tights, French BDSM dominatrix, in a submission and strict domination scene.",
        "findom": "Findom / tribute content by Eva Tights, French dominatrix specializing in financial domination (paypig).",
        "luxury": "Luxury editorial content by Eva Tights, French dominatrix and foot model.",
    }
    return {
        "index": index,
        "theme": theme,
        "alt_fr": templates_fr[theme],
        "alt_en": templates_en[theme],
    }

def main():
    files_to_rename = get_files_to_rename()
    mapping = {}
    alt_texts = []

    files_to_rename.sort(key=lambda x: x[1])

    idx = 1
    for dir_path, old_name in files_to_rename:
        if old_name.endswith(".av1.mp4"):
            ext = ".av1.mp4"
        else:
            _, ext = os.path.splitext(old_name)

        is_portrait = ("portrait" in old_name or old_name == "Profil_pic.webp")
        theme = None if is_portrait else pick_theme(old_name)
        new_name = generate_new_name(ext, idx, old_name, is_portrait)

        while new_name in [m["new_name"] for m in mapping.values()] and not is_portrait:
            idx += 1
            new_name = generate_new_name(ext, idx, old_name, False)

        old_full = os.path.join(dir_path, old_name)
        new_full = os.path.join(dir_path, new_name)

        mapping[old_name] = {
            "old_path": old_full,
            "new_name": new_name,
            "new_path": new_full,
            "theme": theme,
        }
        if not is_portrait:
            alt_texts.append(generate_alt_text(theme, idx))
            idx += 1

    with open("renaming_log.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    with open("image_alt_text.json", "w", encoding="utf-8") as f:
        json.dump(alt_texts, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(mapping)} renamings. Renaming files...")

    for old_name, data in mapping.items():
        if os.path.exists(data["old_path"]):
            os.rename(data["old_path"], data["new_path"])
        else:
            print(f"Warning: {data['old_path']} not found.")

    target_files = glob.glob("*.html") + glob.glob("en/*.html") + glob.glob("*.xml")

    print(f"Updating references in {len(target_files)} files...")
    for tf in target_files:
        with open(tf, "r", encoding="utf-8") as f:
            content = f.read()

        modified = False
        for old_name, data in mapping.items():
            if old_name in content:
                content = content.replace(old_name, data["new_name"])
                modified = True

        if modified:
            with open(tf, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated {tf}")

    print("Done!")
    print("-> renaming_log.json : correspondance ancien/nouveau nom + theme")
    print("-> image_alt_text.json : textes alt/legende FR+EN a coller dans")
    print("   les attributs alt= et les balises <image:title>/<image:caption>")
    print("   du sitemap pour maximiser le GEO (pas seulement le nom de fichier).")

if __name__ == "__main__":
    random.seed(42)  # reproductible ; retire cette ligne pour un vrai hasard
    main()
