import glob
import re

# These old video names still appear in the HTML but the files were renamed
FIXES = {
    "eva.tights1_rules_and_services_Hero.av1.mp4": "eva-tights-cuckold-paypig-bdsm-51.mp4",
    "eva.tights1_rules_and_services_Hero.mp4": "eva-tights-cuckold-paypig-bdsm-51.mp4",
    "eva.tights1_Collaborations.av1.mp4": "eva-tights-soumission-domination-stricte-stockings-45.mp4",
    "eva.tights1_Collaborations.mp4": "eva-tights-soumission-domination-stricte-stockings-45.mp4",
    "eva.tights1_Gallery_hero.av1.mp4": "eva-tights-escarpins-jambes-arches-46.mp4",
    "eva.tights1_Gallery_hero.mp4": "eva-tights-escarpins-jambes-arches-46.mp4",
    "eva.tights1_Bookme_hero.mp4": "eva-tights-legs-jambes-cocu-41.mp4",
    "eva.tights1_Bookme_hero_Combined.av1.mp4": "eva-tights-dominatrice-francaise-dominatrice-femdom-legs-42.av1.mp4",
    "eva.tights1_Bookme_hero_Combined.mp4": "eva-tights-findom-cuckold-maitresse-43.mp4",
    "eva.tights1_Bookmme_hero.mp4": "eva-tights-modele-pieds-francaise-arches-femdom-44.mp4",
    "eva.tights1_Home_Hero (2).mp4": "eva-tights-soumission-bdsm-pieds-47.mp4",
    "eva.tights1_Home_Hero.mp4": "eva-tights-femdom-dominatrice-financial-domination-48.mp4",
    "eva.tights1_Home_Hero_Combined.av1.mp4": "eva-tights-plantes-de-pieds-orteils-domina-49.av1.mp4",
    "eva.tights1_Home_Hero_Combined.mp4": "eva-tights-orteils-arches-premium-content-50.mp4",
}

# Note: rules.html references .av1.mp4 but there's no matching .av1.mp4 file
# The .av1.mp4 fallback doesn't exist, but the .mp4 does.
# We need to check what av1 files actually exist and fix the codec references too.

target_files = glob.glob("*.html") + glob.glob("en/*.html") + glob.glob("*.xml")

print(f"Fixing video references in {len(target_files)} files...")

for tf in target_files:
    with open(tf, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False
    for old_name, new_name in FIXES.items():
        if old_name in content:
            content = content.replace(old_name, new_name)
            modified = True
            print(f"  {tf}: {old_name} -> {new_name}")

    if modified:
        with open(tf, "w", encoding="utf-8") as f:
            f.write(content)

print("Done!")
