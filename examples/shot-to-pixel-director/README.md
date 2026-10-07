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

## Setup checklist

Run these on the machine that has the GPU and ComfyUI.

1. **Prerequisites:** Python 3.12+, git, and an NVIDIA driver (`nvidia-smi` should list your GPU).
2. **Install:**
   ```bash
   git clone https://github.com/vashido-code/ai-agents-for-beginners.git
   cd ai-agents-for-beginners
   python -m venv venv
   venv\Scripts\activate          # Linux/macOS: source venv/bin/activate
   pip install "foundry-local-sdk>=2" httpx jupyter
   ```
   The 2.x SDK bundles the Foundry Local runtime, so a separate Foundry Local install should not be needed. This notebook uses the 2.x API, which differs from the older `FoundryLocalManager(alias)` calls in Lesson 17.
3. **Check the local LLM.** List the catalog and pick a chat model alias; if `qwen2.5-7b` is missing, change `LLM_ALIAS` in the notebook:
   ```python
   from foundry_local_sdk import Configuration, FoundryLocalManager
   FoundryLocalManager.initialize(Configuration(app_name="check"))
   print(sorted({m.alias for m in FoundryLocalManager.instance.catalog.list_models()}))
   ```
   The first run downloads the model.
4. **Check ComfyUI.** It should answer at `http://127.0.0.1:8188` (`curl http://127.0.0.1:8188/system_stats`). First confirm that each of your LTX, Wan and MiniMax graphs generates a video in ComfyUI on its own. Change `COMFY_URL` in the notebook if your port differs.
5. **Export and bind your workflows** (next section).
6. **Dry run:** run the notebook top to bottom with `DRY_RUN = True`. Open a file in `shot_to_pixel_demo/dry_run/final/` and confirm the prompt, size, frame count and seed landed in the right nodes. LTX frame counts should be `8n+1` and Wan `4n+1`.
7. **First live run:** set `DRY_RUN = False`, shrink the script to one short shot, and test one model at a time (LTX draft first). Watch `nvidia-smi`: video generation should use the VRAM, not the LLM.

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
