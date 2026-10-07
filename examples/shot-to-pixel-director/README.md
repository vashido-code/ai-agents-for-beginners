# Shot-to-Pixel Director

A local pre-production and generation agent for ComfyUI video work. Give it a script or an idea and it plans a cinematographer-style shot list, routes each shot to the right video model (LTX, Wan or MiniMax), writes a prompt for each, queues the generations in ComfyUI, and helps you review and revise.

The language model runs in [Foundry Local](https://learn.microsoft.com/azure/ai-foundry/foundry-local/), so planning and prompt writing are free and private. No cloud services or Azure subscription are needed.

Notebook: [`shot-to-pixel-director.ipynb`](./shot-to-pixel-director.ipynb)

## How it works

```
script ──> plan_shots (LLM, validated JSON) ──> route (plain Python)
      ──> LTX drafts for every shot ──> you review / revise / approve
      ──> finals batched by model: LTX, then Wan, then MiniMax
      ──> shotlist.md + shots.json
```

| Intent | Final model | Why |
|---|---|---|
| `standard` | LTX | Fast and cheap |
| `vfx` | Wan | Control, LoRAs, VFX elements |
| `hero` | MiniMax | Key shots worth the slower model |

Every shot is drafted on LTX first, at low resolution and capped at 3 seconds. You judge framing and motion there, then only approved shots get a final pass.

## VRAM strategy (24 GB GPU)

- The LLM is **unloaded before any generation** so ComfyUI has the whole card.
- Jobs are **sorted by model**, so each video model loads once per pass.
- ComfyUI's `/free` endpoint is called **between models**.
- Jobs run **one at a time**.

## Setup

1. Install Foundry Local. This notebook uses the **2.x Python SDK** (`pip install "foundry-local-sdk>=2"`), whose API differs from the `FoundryLocalManager(alias)` calls in Lesson 17.
2. Start ComfyUI (default `http://127.0.0.1:8188`). Not needed while `DRY_RUN = True`.
3. Open the notebook and run it top to bottom. It is in **dry run** mode by default and writes the patched workflow JSON for every job under `shot_to_pixel_demo/dry_run/`.

## Connecting your own ComfyUI workflows

1. In ComfyUI, enable *Settings → Dev mode* and use **Save (API Format)** for your LTX, Wan and MiniMax graphs.
2. Save them in a `workflows/` folder next to the notebook.
3. In the notebook, update `WORKFLOWS[model]["bind"]`. Each entry maps a field (`prompt`, `negative`, `seed`, `width`, `height`, `frames`, `fps`, `prefix`) to `(node_id, input_name)` in your exported JSON. The ids in the notebook are placeholders.
4. Run a single short shot per model and check the result before setting `DRY_RUN = False`.

A wrong node id raises an error rather than silently producing the wrong video.

## Limits

- It cannot watch your clips. Review is `ffprobe` checks (resolution, duration) plus your own judgement.
- The per-model prompt styles, resolutions and frame rates are starting points. LTX (`8n+1` frames) and Wan (`4n+1` frames) frame rules are applied, but the MiniMax profile is unverified against a local build.
- Not covered: character consistency across shots, audio, and assembling the edit.
- The Foundry Local and ComfyUI code paths were tested only with stand-ins (a mocked LLM and a fake ComfyUI server). The first real run on your machine is the real test.
