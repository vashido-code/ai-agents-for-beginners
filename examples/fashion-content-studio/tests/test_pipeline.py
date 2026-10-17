"""End-to-end run on the mock provider: no keys, no GPU. Run: python -m unittest discover tests"""

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image

from studio import config, media, pipeline
from studio.providers import get_provider


class MockPipelineTest(unittest.TestCase):
    def test_full_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            garment = tmp / "shirt.png"
            Image.new("RGB", (600, 700), (40, 90, 160)).save(garment)
            provider = get_provider("mock")

            job = pipeline.Job.create(tmp / "jobs", "SKU1", "top", garment)
            photos = pipeline.make_photos(job, provider)
            self.assertEqual({p["id"] for p in photos}, {"f_studio_slim", "f_studio_plus", "f_street", "m_studio"})

            with self.assertRaises(ValueError):
                pipeline.make_videos(job, provider)  # nothing approved yet
            pipeline.approve(job, ["f_studio_slim", "m_studio"])
            self.assertEqual(len(pipeline.make_videos(job, provider)), 2)

            zip_path = pipeline.make_pack(job, ["wb", "ozon"])
            manifest = json.loads((job.dir / "pack" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["warnings"], [])
            self.assertEqual(len(manifest["files"]), 8)  # 2 photos + 2 videos per marketplace
            with zipfile.ZipFile(zip_path) as z:
                self.assertNotIn("manifest.json", z.namelist())

            for mp in ("wb", "ozon"):
                spec = config.MARKETPLACES[mp]
                photo = next((job.dir / "pack" / mp).glob("*_photo_01.jpg"))
                self.assertEqual(Image.open(photo).size, spec["photo_size"])
                info = media.probe(next((job.dir / "pack" / mp).glob("*_video_01.mp4")))
                self.assertEqual((info["width"], info["height"]), spec["video_size"])
                # 5 s source is ping-ponged to reach the 6 s minimum
                self.assertGreaterEqual(info["duration"], spec["video_min_s"])

    def test_category_filters_personas(self):
        ids = {p["id"] for p in pipeline.load_personas("dress")}
        self.assertNotIn("m_studio", ids)


if __name__ == "__main__":
    unittest.main()
