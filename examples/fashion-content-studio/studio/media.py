"""Image and video helpers: fit to marketplace formats and check the result."""

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps


def fit_photo(src: Path, dest: Path, size: tuple[int, int]) -> dict:
    """Fit an image into `size` without cropping the garment: contain on a blurred fill of itself."""
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = size
    background = ImageOps.fit(img, size).filter(ImageFilter.GaussianBlur(40))
    fg = ImageOps.contain(img, size, Image.Resampling.LANCZOS)
    background.paste(fg, ((w - fg.width) // 2, (h - fg.height) // 2))
    dest.parent.mkdir(parents=True, exist_ok=True)
    background.save(dest, "JPEG", quality=92)
    # Upscaling a small source does not add detail; report it so the operator can regenerate.
    return {"upscaled": img.width < fg.width or img.height < fg.height}


def fit_video(src: Path, dest: Path, size: tuple[int, int], min_s: float, max_s: float) -> None:
    """Scale a clip into `size` over a blurred fill, ping-pong it if shorter than `min_s`, cap at `max_s`."""
    w, h = size
    duration = probe(src)["duration"]
    loop = duration < min_s
    chain = "[0:v]split[f][r];[r]reverse[rv];[f][rv]concat=n=2:v=1[src];" if loop else "[0:v]null[src];"
    chain += (
        f"[src]split[a][b];"
        f"[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=30[bg];"
        f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[out]"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter_complex", chain,
         "-map", "[out]", "-an", "-t", str(max_s), "-c:v", "libx264", "-preset", "medium",
         "-crf", "20", "-movflags", "+faststart", str(dest)],
        check=True,
    )


def probe(path: Path) -> dict:
    """Width, height and duration of a video via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    stream = data["streams"][0]
    return {"width": stream["width"], "height": stream["height"],
            "duration": float(data["format"]["duration"])}
