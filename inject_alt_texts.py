import json
import re
import glob

# Load alt texts
with open("image_alt_text.json", "r", encoding="utf-8") as f:
    alt_data = json.load(f)

alt_map = {item["index"]: item for item in alt_data}

def update_html(filepath, is_en=False):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    def replacer(match):
        img_tag = match.group(0)
        # extract index from src
        m_src = re.search(r'src="(?:\.\./)?assets/webp/[^"]+-(\d{2})\.webp"', img_tag)
        if m_src:
            idx = int(m_src.group(1))
            if idx in alt_map:
                new_alt = alt_map[idx]["alt_en"] if is_en else alt_map[idx]["alt_fr"]
                # Escape quotes if necessary, though alt text shouldn't have unescaped quotes
                new_alt = new_alt.replace('"', '&quot;')
                if 'alt="' in img_tag:
                    img_tag = re.sub(r'alt="[^"]*"', f'alt="{new_alt}"', img_tag)
                else:
                    # insert alt attribute if missing
                    img_tag = img_tag.replace('<img ', f'<img alt="{new_alt}" ')
        return img_tag

    new_content = re.sub(r'<img\s+[^>]+>', replacer, content)
    
    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for f in glob.glob("*.html"):
    update_html(f, is_en=False)
for f in glob.glob("en/*.html"):
    update_html(f, is_en=True)

# For sitemap.xml
try:
    with open("sitemap.xml", "r", encoding="utf-8") as f:
        sitemap = f.read()

    def sitemap_replacer(match):
        block = match.group(0)
        m_loc = re.search(r'<image:loc>.*?-(\d{2})\.webp</image:loc>', block)
        if m_loc:
            idx = int(m_loc.group(1))
            if idx in alt_map:
                new_title = alt_map[idx]["alt_fr"]
                new_title = new_title.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                
                if "<image:title>" in block:
                    block = re.sub(r'<image:title>.*?</image:title>', f'<image:title>{new_title}</image:title>', block)
                else:
                    block = block.replace("</image:loc>", f"</image:loc>\n      <image:title>{new_title}</image:title>")
        return block

    new_sitemap = re.sub(r'<image:image>.*?</image:image>', sitemap_replacer, sitemap, flags=re.DOTALL)
    if new_sitemap != sitemap:
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(new_sitemap)
        print("Updated sitemap.xml")
except FileNotFoundError:
    print("sitemap.xml not found")

print("Injection complete.")
