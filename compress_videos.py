from pathlib import Path
import subprocess

INPUT_DIR = Path("assets/Vid")
OUTPUT_DIR = Path("assets/Vid_optimized")

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".wmv",
    ".m4v",
    ".flv",
    ".webm"
}

OUTPUT_DIR.mkdir(exist_ok=True)

def encode_av1(input_file, output_file):
    subprocess.run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-stats",

        "-i", str(input_file),

        "-map_metadata", "-1",

        "-c:v", "libsvtav1",
        "-crf", "30",
        "-preset", "6",

        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "128k",

        "-movflags", "+faststart",

        "-y",
        str(output_file)
    ])


def encode_h264(input_file, output_file):
    subprocess.run([
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-stats",

        "-i", str(input_file),

        "-map_metadata", "-1",

        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "22",

        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "128k",

        "-movflags", "+faststart",

        "-y",
        str(output_file)
    ])


for file in INPUT_DIR.rglob("*"):

    if file.suffix.lower() not in VIDEO_EXTENSIONS:
        continue

    relative = file.relative_to(INPUT_DIR)

    av1 = OUTPUT_DIR / relative.with_suffix(".av1.mp4")
    h264 = OUTPUT_DIR / relative.with_suffix(".mp4")

    av1.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nEncoding {file.name}")

    encode_av1(file, av1)
    encode_h264(file, h264)

    original = file.stat().st_size
    av1_size = av1.stat().st_size
    h264_size = h264.stat().st_size

    print(f"Original : {original/1024/1024:.2f} MB")
    print(f"AV1      : {av1_size/1024/1024:.2f} MB")
    print(f"H264     : {h264_size/1024/1024:.2f} MB")

print("\nFinished.")
