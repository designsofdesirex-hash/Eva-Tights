from pathlib import Path
import subprocess

INPUT_DIR = Path("assets/Vid_optimized")
OUTPUT_DIR = Path("assets/Vid_optimized")

pairs_to_merge = [
    {
        "name": "eva.tights1_Home_Hero",
        "files": [
            "eva.tights1_Home_Hero.mp4",
            "eva.tights1_Home_Hero (2).mp4"
        ]
    },
    {
        "name": "eva.tights1_Bookme_hero",
        "files": [
            "eva.tights1_Bookme_hero.mp4",
            "eva.tights1_Bookmme_hero.mp4"
        ]
    }
]

for pair in pairs_to_merge:
    name = pair["name"]
    files = pair["files"]
    
    print(f"\nMerging and encoding {name}...")
    
    concat_txt_path = INPUT_DIR / f"{name}_concat.txt"
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for fname in files:
            f.write(f"file '{fname}'\n")
            
    output_base = OUTPUT_DIR / f"{name}_Combined"
    
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
        "-f", "concat", "-safe", "0", "-i", f"{name}_concat.txt",
        "-map_metadata", "-1",
        "-c:v", "libx264", "-preset", "slow", "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-y",
        str(output_base.absolute()) + ".mp4"
    ], cwd=str(INPUT_DIR.absolute()))
    
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
        "-f", "concat", "-safe", "0", "-i", f"{name}_concat.txt",
        "-map_metadata", "-1",
        "-c:v", "libsvtav1", "-preset", "6", "-crf", "30",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-y",
        str(output_base.absolute()) + ".av1.mp4"
    ], cwd=str(INPUT_DIR.absolute()))

    concat_txt_path.unlink()

print("\nDone merging and encoding.")
