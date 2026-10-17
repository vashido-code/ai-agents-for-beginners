"""Offline stand-in: runs the whole pipeline with no keys, no GPU and no cost.

The output only proves the plumbing (files, formats, manifest). It is not a preview of quality.
"""

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

# Where the garment goes on the person image, as fractions of width/height.
_BOXES = {
    "top": (0.25, 0.22, 0.75, 0.55),
    "outerwear": (0.22, 0.2, 0.78, 0.6),
    "dress": (0.25, 0.22, 0.75, 0.85),
    "bottom": (0.28, 0.5, 0.72, 0.92),
}


class MockProvider:
    name = "mock"

    def try_on(self, person: Path, garment: Path, category: str, out: Path) -> Path:
        base = Image.open(person).convert("RGB")
        x0, y0, x1, y1 = _BOXES[category]
        box = (int(x0 * base.width), int(y0 * base.height), int(x1 * base.width), int(y1 * base.height))
        cloth = ImageOps.contain(Image.open(garment).convert("RGB"), (box[2] - box[0], box[3] - box[1]))
        base.paste(cloth, (box[0] + (box[2] - box[0] - cloth.width) // 2, box[1]))
        ImageDraw.Draw(base).text((10, 10), "MOCK TRY-ON", fill=(255, 0, 0))
        out.parent.mkdir(parents=True, exist_ok=True)
        base.save(out, "JPEG", quality=92)
        return out

    def image_to_video(self, image: Path, prompt: str, negative: str, seconds: int, out: Path) -> Path:
        w, h = Image.open(image).size
        w, h = w - w % 2, h - h % 2
        fps = 24
        frames = seconds * fps
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image),
             "-vf", f"zoompan=z='min(zoom+0.0012,1.12)':d={frames}:s={w}x{h}:fps={fps},format=yuv420p",
             "-frames:v", str(frames), "-c:v", "libx264", str(out)],
            check=True,
        )
        return out


def placeholder_person(dest: Path, label: str) -> Path:
    """A grey silhouette standing in for a model photo when none was added yet (mock only)."""
    img = Image.new("RGB", (960, 1280), (226, 222, 216))
    d = ImageDraw.Draw(img)
    d.ellipse((405, 112, 555, 275), fill=(150, 140, 132))
    d.rounded_rectangle((312, 288, 648, 800), radius=75, fill=(150, 140, 132))
    d.rectangle((362, 788, 462, 1200), fill=(150, 140, 132))
    d.rectangle((498, 788, 598, 1200), fill=(150, 140, 132))
    d.text((10, 1250), f"placeholder: {label}", fill=(60, 60, 60))
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=92)
    return dest
