import glob
import re

# Full keyword sets per language
KEYWORDS_FR = (
    "Eva Tights, foot fetish, feet fetish, femdom, bdsm, domina, dominatrice, "
    "dominatrice française, nylon, stockings, bas nylon, collants, pieds, "
    "soumis, soumission, cocu, cuckold, paypig, findom, domination financière, "
    "vente de photos de pieds, talons, talons aiguilles, modèle de pieds française, "
    "domination, contenu éditorial fetish, dominatrice en ligne"
)

KEYWORDS_EN = (
    "Eva Tights, foot fetish, feet fetish, femdom, bdsm, domina, dominatrix, "
    "French dominatrix, nylon, stockings, nylon stockings, pantyhose, feet, "
    "submissive, submission, cuckold, paypig, findom, financial domination, "
    "feet pics, feet photos, heels, stiletto heels, French foot model, "
    "domination, editorial fetish content, online dominatrix"
)

def update_keywords(filepath, new_keywords):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'<meta\s+name="keywords"\s+content="[^"]*"\s*/?\s*>'
    replacement = f'<meta name="keywords" content="{new_keywords}" />'

    new_content, count = re.subn(pattern, replacement, content, count=1)

    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
    else:
        print(f"No keywords tag found: {filepath}")

# FR pages (root)
for f in glob.glob("*.html"):
    update_keywords(f, KEYWORDS_FR)

# EN pages
for f in glob.glob("en/*.html"):
    update_keywords(f, KEYWORDS_EN)

print("Done!")
