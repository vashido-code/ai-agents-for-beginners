"""garment photo -> try-on on model photos -> operator picks -> video -> marketplace pack.

A job is one look (one garment) for one client. Its state lives in `<jobs>/<sku>/job.json`, so each
step can be re-run on its own and the operator can review the photos before paying for video.
"""

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from . import config, media
from .providers import Provider

ROOT = Path(__file__).resolve().parents[1]
PERSONAS_DIR = ROOT / "personas"


class Job:
    def __init__(self, path: Path):
        self.dir = path
        if not (path / "job.json").exists():
            raise FileNotFoundError(f"No job in {path}. Create it with `new` first.")
        self.state = json.loads((path / "job.json").read_text(encoding="utf-8"))

    @classmethod
    def create(cls, jobs_dir: Path, sku: str, category: str, garment: Path) -> "Job":
        if category not in config.CATEGORIES:
            raise ValueError(f"category must be one of {config.CATEGORIES}")
        path = jobs_dir / sku
        if (path / "job.json").exists():
            raise FileExistsError(f"Job {sku} already exists in {path}")
        (path / "input").mkdir(parents=True)
        stored = path / "input" / f"garment{garment.suffix.lower()}"
        shutil.copy(garment, stored)
        state = {"sku": sku, "category": category, "garment": str(stored.relative_to(path)),
                 "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "photos": [], "videos": [], "costs": []}
        (path / "job.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        return cls(path)

    def save(self) -> None:
        (self.dir / "job.json").write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")

    def charge(self, provider: Provider, step: str, rub: float) -> None:
        self.state["costs"].append({"step": step, "provider": provider.name, "rub": rub})


def load_personas(category: str, only: list[str] | None = None) -> list[dict]:
    personas = json.loads((PERSONAS_DIR / "personas.json").read_text(encoding="utf-8"))
    chosen = [p for p in personas if category in p["fits"] and (not only or p["id"] in only)]
    if not chosen:
        raise ValueError(f"No persona in personas.json fits '{category}'" + (f" among {only}" if only else ""))
    return chosen


def _persona_image(job: Job, persona: dict, provider: Provider) -> Path:
    path = PERSONAS_DIR / persona["file"]
    if path.exists():
        return path
    if provider.name == "mock":
        from .providers.mock import placeholder_person
        return placeholder_person(job.dir / "input" / f"persona_{persona['id']}.jpg", persona["id"])
    raise FileNotFoundError(f"{path} is missing. Add the model photo (see personas/README.md).")


def make_photos(job: Job, provider: Provider, personas: list[str] | None = None) -> list[dict]:
    """Try the garment on every matching persona. Re-running replaces earlier photos of the same persona."""
    garment = job.dir / job.state["garment"]
    made = []
    for persona in load_personas(job.state["category"], personas):
        out = job.dir / "photos" / f"{persona['id']}.jpg"
        print(f"  try-on: {persona['id']} ...", flush=True)
        provider.try_on(_persona_image(job, persona, provider), garment, job.state["category"], out)
        job.charge(provider, f"try_on:{persona['id']}", config.COSTS_RUB[provider.name]["try_on"])
        job.state["photos"] = [p for p in job.state["photos"] if p["id"] != persona["id"]]
        photo = {"id": persona["id"], "file": str(out.relative_to(job.dir)), "approved": False}
        job.state["photos"].append(photo)
        made.append(photo)
        job.save()
    return made


def approve(job: Job, ids: list[str]) -> None:
    known = {p["id"] for p in job.state["photos"]}
    unknown = set(ids) - known
    if unknown:
        raise ValueError(f"No photos for {sorted(unknown)}. Available: {sorted(known)}")
    for p in job.state["photos"]:
        p["approved"] = p["id"] in ids
    job.save()


def make_videos(job: Job, provider: Provider) -> list[dict]:
    """One clip per approved photo. Video is the expensive step, so nothing runs without approval."""
    approved = [p for p in job.state["photos"] if p["approved"]]
    if not approved:
        raise ValueError("No approved photos. Review photos/ and run `approve` first.")
    seconds = config.VIDEO_SECONDS
    made = []
    for photo in approved:
        out = job.dir / "videos" / f"{photo['id']}.mp4"
        print(f"  video: {photo['id']} ({seconds}s) ...", flush=True)
        provider.image_to_video(job.dir / photo["file"], config.VIDEO_PROMPTS[job.state["category"]],
                                config.VIDEO_NEGATIVE, seconds, out)
        job.charge(provider, f"video:{photo['id']}", config.COSTS_RUB[provider.name]["video_per_s"] * seconds)
        job.state["videos"] = [v for v in job.state["videos"] if v["id"] != photo["id"]]
        video = {"id": photo["id"], "file": str(out.relative_to(job.dir))}
        job.state["videos"].append(video)
        made.append(video)
        job.save()
    return made


def make_pack(job: Job, marketplaces: list[str]) -> Path:
    """Export approved photos and all videos in each marketplace's format, check them, zip them."""
    photos = [p for p in job.state["photos"] if p["approved"]] or job.state["photos"]
    if not photos:
        raise ValueError("No photos yet. Run `photos` first.")
    pack_dir = job.dir / "pack"
    shutil.rmtree(pack_dir, ignore_errors=True)
    files, warnings = [], []
    for mp in marketplaces:
        spec = config.MARKETPLACES[mp]
        for i, photo in enumerate(photos, 1):
            dest = pack_dir / mp / f"{job.state['sku']}_{mp}_photo_{i:02d}.jpg"
            if media.fit_photo(job.dir / photo["file"], dest, spec["photo_size"])["upscaled"]:
                warnings.append(f"{dest.name}: source smaller than {spec['photo_size']}, upscaled")
            files.append(dest)
        for i, video in enumerate(job.state["videos"], 1):
            dest = pack_dir / mp / f"{job.state['sku']}_{mp}_video_{i:02d}.mp4"
            media.fit_video(job.dir / video["file"], dest, spec["video_size"], spec["video_min_s"], spec["video_max_s"])
            info = media.probe(dest)
            if (info["width"], info["height"]) != spec["video_size"] or not (
                    spec["video_min_s"] - 0.1 <= info["duration"] <= spec["video_max_s"] + 0.1):
                warnings.append(f"{dest.name}: {info} does not match {spec['label']} requirements")
            files.append(dest)

    cost = round(sum(c["rub"] for c in job.state["costs"]), 2)
    price = config.PRICE_PER_LOOK_RUB
    manifest = {
        "sku": job.state["sku"], "category": job.state["category"],
        "marketplaces": marketplaces, "files": [str(f.relative_to(pack_dir)) for f in files],
        "warnings": warnings,
        "economics_rub": {"cost": cost, "price": price, "margin": price - cost,
                          "margin_pct": round(100 * (price - cost) / price, 1) if price else None},
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    zip_path = job.dir / f"{job.state['sku']}_pack.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:  # the manifest holds our costs, so it stays out of the client's zip
            z.write(f, f.relative_to(pack_dir))
    return zip_path
