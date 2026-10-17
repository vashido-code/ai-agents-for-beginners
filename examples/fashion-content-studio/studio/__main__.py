"""Command line for the operator. Run `python -m studio --help` from the example folder."""

import argparse
import json
import os
import sys
from pathlib import Path

from . import config, pipeline
from .providers import get_provider


def main() -> None:
    parser = argparse.ArgumentParser(prog="studio", description="Garment photo -> AI model photos -> video -> marketplace pack")
    parser.add_argument("--jobs", type=Path, default=Path(os.getenv("STUDIO_JOBS_DIR", "jobs")))
    parser.add_argument("--provider", default=os.getenv("STUDIO_PROVIDER", "mock"), choices=["mock", "kling", "comfyui"])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="create a job for one look")
    p.add_argument("sku")
    p.add_argument("garment", type=Path, help="photo of the garment (flat lay, hanger or mannequin)")
    p.add_argument("--category", required=True, choices=config.CATEGORIES)

    p = sub.add_parser("photos", help="try the garment on the model photos")
    p.add_argument("sku")
    p.add_argument("--personas", help="comma-separated persona ids (default: all that fit)")

    p = sub.add_parser("approve", help="mark the photos to keep (videos are made only from these)")
    p.add_argument("sku")
    p.add_argument("ids", help="comma-separated persona ids")

    p = sub.add_parser("video", help="make a clip from each approved photo")
    p.add_argument("sku")

    p = sub.add_parser("pack", help="export for marketplaces and zip")
    p.add_argument("sku")
    p.add_argument("--marketplaces", default=",".join(config.MARKETPLACES))

    p = sub.add_parser("run", help="all steps in one go, approving the first N photos (for demos)")
    p.add_argument("sku")
    p.add_argument("garment", type=Path)
    p.add_argument("--category", required=True, choices=config.CATEGORIES)
    p.add_argument("--videos", type=int, default=1, help="how many photos to turn into video")
    p.add_argument("--marketplaces", default=",".join(config.MARKETPLACES))

    p = sub.add_parser("status", help="show a job")
    p.add_argument("sku")

    args = parser.parse_args()
    split = lambda s: [x.strip() for x in s.split(",") if x.strip()]  # noqa: E731

    if args.cmd in ("new", "run"):
        job = pipeline.Job.create(args.jobs, args.sku, args.category, args.garment)
        print(f"Job created: {job.dir}")
        if args.cmd == "new":
            return
    else:
        job = pipeline.Job(args.jobs / args.sku)

    if args.cmd in ("photos", "run"):
        provider = get_provider(args.provider)
        photos = pipeline.make_photos(job, provider, split(args.personas) if getattr(args, "personas", None) else None)
        print(f"{len(photos)} photo(s) in {job.dir / 'photos'}")
        if args.cmd == "photos":
            print(f"Review them, then: python -m studio approve {job.state['sku']} <ids>")
            return
        pipeline.approve(job, [p["id"] for p in photos[:args.videos]])

    if args.cmd == "approve":
        pipeline.approve(job, split(args.ids))
        print("Approved:", [p["id"] for p in job.state["photos"] if p["approved"]])
        return

    if args.cmd in ("video", "run"):
        videos = pipeline.make_videos(job, get_provider(args.provider))
        print(f"{len(videos)} video(s) in {job.dir / 'videos'}")
        if args.cmd == "video":
            return

    if args.cmd in ("pack", "run"):
        zip_path = pipeline.make_pack(job, split(args.marketplaces))
        manifest = json.loads((job.dir / "pack" / "manifest.json").read_text(encoding="utf-8"))
        print(f"Pack: {zip_path}")
        for w in manifest["warnings"]:
            print(f"  WARNING {w}")
        e = manifest["economics_rub"]
        print(f"Cost {e['cost']} RUB, price {e['price']} RUB, margin {e['margin']} RUB ({e['margin_pct']}%)")
        return

    if args.cmd == "status":
        print(json.dumps(job.state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, FileExistsError, KeyError) as e:
        sys.exit(f"Error: {e}")
