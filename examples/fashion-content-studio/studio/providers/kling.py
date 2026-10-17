"""Kling API: Kolors virtual try-on for photos, image-to-video for the clip.

Written against Kling's public API docs (JWT auth, task create + poll) but NOT run against the
live API yet. Check endpoint paths and model names in your Kling console before the first paid
run, and start with one look. Paying Kling from Russia needs a foreign card or an intermediary;
an aggregator with a Kling-compatible API can be used by changing KLING_API_BASE.
"""

import base64
import os
import time
from pathlib import Path

import httpx
import jwt


class KlingProvider:
    name = "kling"

    def __init__(self):
        self.access_key = os.environ["KLING_ACCESS_KEY"]
        self.secret_key = os.environ["KLING_SECRET_KEY"]
        self.base = os.getenv("KLING_API_BASE", "https://api-singapore.klingai.com").rstrip("/")
        self.tryon_model = os.getenv("KLING_TRYON_MODEL", "kolors-virtual-try-on-v1-5")
        self.video_model = os.getenv("KLING_VIDEO_MODEL", "kling-v2-1")
        self.video_mode = os.getenv("KLING_VIDEO_MODE", "std")  # std is cheaper, pro is sharper

    def _headers(self) -> dict:
        now = int(time.time())
        token = jwt.encode({"iss": self.access_key, "exp": now + 1800, "nbf": now - 5},
                           self.secret_key, algorithm="HS256", headers={"typ": "JWT"})
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _run(self, path: str, body: dict, timeout_s: int) -> dict:
        r = httpx.post(f"{self.base}{path}", json=body, headers=self._headers(), timeout=60)
        r.raise_for_status()
        task_id = _data(r)["task_id"]
        start = time.time()
        while time.time() - start < timeout_s:
            time.sleep(5)
            r = httpx.get(f"{self.base}{path}/{task_id}", headers=self._headers(), timeout=60)
            r.raise_for_status()
            data = _data(r)
            status = data.get("task_status")
            if status == "succeed":
                return data["task_result"]
            if status == "failed":
                raise RuntimeError(f"Kling task {task_id} failed: {data.get('task_status_msg')}")
        raise TimeoutError(f"Kling task {task_id} did not finish within {timeout_s}s")

    def try_on(self, person: Path, garment: Path, category: str, out: Path) -> Path:
        result = self._run("/v1/images/kolors-virtual-try-on", {
            "model_name": self.tryon_model,
            "human_image": _b64(person),
            "cloth_image": _b64(garment),
        }, timeout_s=600)
        return _download(result["images"][0]["url"], out)

    def image_to_video(self, image: Path, prompt: str, negative: str, seconds: int, out: Path) -> Path:
        result = self._run("/v1/videos/image2video", {
            "model_name": self.video_model,
            "mode": self.video_mode,
            "image": _b64(image),
            "prompt": prompt,
            "negative_prompt": negative,
            "duration": str(seconds),
        }, timeout_s=1800)
        return _download(result["videos"][0]["url"], out)


def _data(r: httpx.Response) -> dict:
    payload = r.json()
    if payload.get("code") not in (0, None):
        raise RuntimeError(f"Kling API error {payload.get('code')}: {payload.get('message')}")
    return payload["data"]


def _b64(path: Path) -> str:
    # Kling expects raw base64, without a "data:image/...;base64," prefix.
    return base64.b64encode(path.read_bytes()).decode()


def _download(url: str, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=300, follow_redirects=True) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return out
