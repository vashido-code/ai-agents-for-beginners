"""Self-hosted ComfyUI: your own try-on and image-to-video graphs on your own (or rented) GPU.

This is the path that does not depend on paying a foreign API. Build two graphs in ComfyUI
(for example a CatVTON / IDM-VTON try-on graph and a Wan 2.x image-to-video graph), export
each with Settings -> Dev mode -> "Save (API Format)", put them in `workflows/` and fill in the
node ids below. The ids are placeholders. A wrong id raises an error instead of silently
producing the wrong output.
"""

import json
import os
import random
import time
import uuid
from pathlib import Path

import httpx

WORKFLOW_DIR = Path(__file__).resolve().parents[2] / "workflows"

# EDIT ME: field -> (node_id, input_name) in your exported API-format workflow.
WORKFLOWS = {
    "try_on": {"file": "tryon_api.json", "bind": {
        "person": ("10", "image"), "garment": ("11", "image"), "seed": ("20", "seed"),
        "prefix": ("30", "filename_prefix")}},
    "video": {"file": "i2v_api.json", "bind": {
        "image": ("10", "image"), "prompt": ("6", "text"), "negative": ("7", "text"),
        "seed": ("3", "seed"), "frames": ("20", "length"), "prefix": ("30", "filename_prefix")}},
}
VIDEO_FPS = 16  # Wan 2.x native rate; frames must be 4n+1


class ComfyUIProvider:
    name = "comfyui"

    def __init__(self):
        self.url = os.getenv("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")
        self.client_id = uuid.uuid4().hex

    def try_on(self, person: Path, garment: Path, category: str, out: Path) -> Path:
        return self._generate("try_on", {
            "person": self._upload(person), "garment": self._upload(garment),
            "seed": random.randint(0, 2**31), "prefix": f"studio_tryon_{out.stem}",
        }, out)

    def image_to_video(self, image: Path, prompt: str, negative: str, seconds: int, out: Path) -> Path:
        frames = round(seconds * VIDEO_FPS / 4) * 4 + 1
        return self._generate("video", {
            "image": self._upload(image), "prompt": prompt, "negative": negative,
            "seed": random.randint(0, 2**31), "frames": frames, "prefix": f"studio_video_{out.stem}",
        }, out)

    def _generate(self, kind: str, values: dict, out: Path) -> Path:
        spec = WORKFLOWS[kind]
        path = WORKFLOW_DIR / spec["file"]
        if not path.exists():
            raise FileNotFoundError(f"{path} not found. Export your {kind} graph with 'Save (API Format)'.")
        workflow = patch_workflow(json.loads(path.read_text(encoding="utf-8")), spec["bind"], values)
        r = httpx.post(f"{self.url}/prompt", json={"prompt": workflow, "client_id": self.client_id}, timeout=30)
        r.raise_for_status()
        files = self._wait(r.json()["prompt_id"])
        if not files:
            raise RuntimeError(f"ComfyUI finished the {kind} graph but saved no output file.")
        return self._download(files[-1], out)

    def _upload(self, path: Path) -> str:
        with path.open("rb") as f:
            r = httpx.post(f"{self.url}/upload/image", files={"image": (path.name, f)},
                           data={"overwrite": "true"}, timeout=60)
        r.raise_for_status()
        info = r.json()
        return f"{info['subfolder']}/{info['name']}" if info.get("subfolder") else info["name"]

    def _wait(self, prompt_id: str, timeout_s: int = 3600) -> list[dict]:
        start = time.time()
        while time.time() - start < timeout_s:
            history = httpx.get(f"{self.url}/history/{prompt_id}", timeout=30).json()
            if prompt_id in history:
                entry = history[prompt_id]
                if entry.get("status", {}).get("status_str") == "error":
                    raise RuntimeError(f"ComfyUI reported an error for {prompt_id}: {entry['status']}")
                files = []
                for node_output in entry.get("outputs", {}).values():
                    for value in node_output.values():
                        if isinstance(value, list):
                            files += [f for f in value if isinstance(f, dict) and "filename" in f
                                      and f.get("type", "output") == "output"]
                return files
            time.sleep(3)
        raise TimeoutError(f"{prompt_id} did not finish within {timeout_s}s")

    def _download(self, file: dict, out: Path) -> Path:
        r = httpx.get(f"{self.url}/view", params={
            "filename": file["filename"], "subfolder": file.get("subfolder", ""), "type": "output"}, timeout=300)
        r.raise_for_status()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(r.content)
        return out


def patch_workflow(workflow: dict, bind: dict, values: dict) -> dict:
    wf = json.loads(json.dumps(workflow))  # deep copy
    for key, value in values.items():
        node, name = bind[key]
        if node not in wf:
            raise KeyError(f"Binding '{key}' points at node {node}, which is not in the workflow.")
        wf[node].setdefault("inputs", {})[name] = value
    return wf
