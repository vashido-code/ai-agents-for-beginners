# Niche local AI for 3D, game engines and game mods (2025-2026)

Scope note: about 9 web searches, mostly search-engine summaries. I fetched no pages in full, so treat dates, VRAM numbers and capability claims as unverified until someone checks the primary repo. Excluded as mainstream, per the brief: blender-mcp (ahujasid), TRELLIS v1, basic Hunyuan3D 2.0, Mantella and generic ComfyUI.

## Which new Blender/UE5 AI agent or MCP projects exist and how capable?

### Takeaway
Unreal Engine now has a crowded field of MCP servers. They range from about 49 tools to over 400, cover UE 5.0 to 5.8, and some need no C++ build. On the Blender side, the interesting work is research agents (LL3M, VIGA) and small fine-tuned bpy models (BlenderLLM, Bioinspired3D), not more MCP bridges. Every one of these runs on Windows. The fine-tuned models (7B and 3B) fit easily on a 24GB card.

### Cited Findings
- **ChiR24/Unreal_mcp** is a TypeScript MCP server. Early versions drove the editor through the Remote Control API (assets, actors, PIE, levels, Sequencer, console) on UE 5.0–5.6. Later versions use a native C++ "Automation Bridge" plugin and add Docker and a GraphQL API. — [GitHub](https://github.com/chir24/unreal_mcp); [Glama](https://glama.ai/mcp/servers/@ChiR24/Unreal_mcp/tree/26946f91de74264f0db2aad8c73c3a86e4f2b50e)
- **unreal-engine-mcp (PyPI)** needs no C++ plugin. It uses the built-in Python Editor Script Plugin plus the Remote Control API, and it adds a local process layer for creating projects, compiling C++, running PIE and packaging. — [PyPI](https://pypi.org/project/unreal-engine-mcp/)
- **ivanmurzak/Unreal-MCP** targets UE 5.7. Agents can spawn actors, edit levels, author Blueprints, edit and compile C++, and take screenshots. It is in beta. — [mcpservers.org](https://mcpservers.org/servers/ivanmurzak/unreal-mcp)
- **remiphilippe/mcp-unreal** is written in Go, exposes 49 tools for UE 5.7, and requires the Remote Control API plugin. — [mcpservers.org](https://mcpservers.org/servers/remiphilippe/mcp-unreal)
- **ue-mcp (chengdagong)** is built on FastMCP and uses Python remote execution. Each server instance is tied to one project. — [Glama](https://glama.ai/mcp/servers/@chengdagong/ue-mcp/blob/f3056c6e01b130c26226b134248804b89fa6f3d7/README.md)
- **StraySpark Unreal MCP Server** is a commercial-style plugin, not clearly open source. It claims more than 400 tools over JSON-RPC, targets UE 5.7 and 5.8, lists v4.5.0 as released 2026-06-22, and says it interoperates with "Epic's first-party MCP plugin". — [StraySpark](https://www.strayspark.studio/docs/unreal-mcp-server). UNVERIFIED: I could not confirm that Epic ships its own MCP plugin. A blog says UE 5.7 shipped an experimental in-editor AI Assistant but does not say it speaks MCP. — [Vaughan blog](https://codex.danielvaughan.com/2026/05/28/codex-cli-unreal-engine-5-7-game-development-mcp-servers-blueprint-agent-workflows/)
- **LL3M** (UChicago, threedle) is a multi-agent system that writes Blender Python to build 3D assets. The authors used Blender 4.4. The hosted server was shut down because Claude 3.7 Sonnet was retired, but setup instructions remain in the repo. — [GitHub](https://github.com/threedle/ll3m); [arXiv 2508.08228](https://arxiv.org/abs/2508.08228v1)
- **VIGA** (Vision-as-Inverse-Graphics Agent, January 2026; Berkeley, CMU, MPI) runs a write-code, render, compare loop against a reference image. It is training-free and reports gains over one-shot baselines on BlenderGym, and it introduces a new benchmark called BlenderBench. I could not confirm a public code repo. — [arXiv 2601.11109](https://arxiv.org/pdf/2601.11109)
- **BlenderLLM** fine-tunes Qwen2.5-Coder-7B on BlendNet (12k instruction/CAD-script pairs) with self-improvement. It dates from December 2024, so it is older than the brief prefers. — [HF](https://huggingface.co/pixofix/BlenderLLM)
- **Bioinspired3D** is a LoRA on Llama-3.2-3B for Blender code that builds bioinspired models. It claims about a 4x gain over its base model. I only saw it on an HF mirror. — [mirror](https://huggingface-gw-kz.just-ai.com/lamm-mit/Bioinspired3D)
- **Sparse-AST / BWM "Blender World Model"** is an HF model that claims Blender 5.1 support, but its reported metrics are internally inconsistent. FLAG: treat as suspect. — [HF](https://huggingface.co/Chaman1234/Sparse-AST-BWM)

### Inferences
- For a 4090 on Windows, the realistic stack is a local coder LLM (or BlenderLLM at 7B) driving one of the no-compile UE MCP servers, or driving Blender directly. The VIGA-style render-and-verify loop needs a vision model, which a 24GB card can still serve at roughly the 7–14B size.

### Gaps
- I did not check GitHub stars, last-commit dates or licenses for any of these.
- I found no newer bpy fine-tunes from 2026.
- I found nothing on local-LLM AI NPC plugins for UE5.

## Which newest image/video-to-3D or world-generation models run on a 4090?

### Takeaway
The best open releases from late 2025 to 2026 come from Microsoft (TRELLIS.2) and Tencent (HY-World 2.0/WorldMirror, Hunyuan3D 2.1+). All of them are reported to fit in 16–24GB. Two caveats matter: the Tencent licenses exclude the EU, UK and South Korea, and the VRAM figures come from secondary sources.

### Cited Findings
- **TRELLIS.2** (Microsoft, December 2025): 4B parameters, MIT license, single image to 3D with full PBR, GLB textures up to 4096², and native ComfyUI support. Sources disagree on VRAM: [cinevva](https://app.cinevva.com/guides/ai-3d-model-generation-timeline-2026) says 24GB, while [cmarix](https://www.cmarix.com/blog/top-open-source-ai-models-for-3d-image-generation/) says at least 16GB. — [Comfy blog](https://blog.comfy.org/p/trellis2-and-pixal3d-are-now-native)
- The same Comfy post says **Pixal3D** is also native in ComfyUI. I found no details on it. — [Comfy blog](https://blog.comfy.org/p/trellis2-and-pixal3d-are-now-native)
- The **Tencent Hunyuan3D releases** (2.1, Omni, Part) ship under a Community License that does not apply in the EU, UK or South Korea. — [cinevva](https://app.cinevva.com/guides/ai-3d-model-generation-timeline-2026)
- **WorldMirror 1.1** (Tencent, October 2025) is a feed-forward model that builds 3D from multi-view or video input, with real-time deployment on one GPU. — [TechNode](https://technode.com/2025/10/22/tencents-worldmirror-1-1-3d-generation-model-enables-single-gpu-real-time-deployment/)
- **HY-World 2.0** releases all weights and code. — [Tencent PDF](https://3d-models.hunyuan.tencent.com/world/world2_0/HY_World_2_0.pdf). A secondary guide says the first public weights are WorldMirror 2.0 at about 1.2B parameters, needing roughly 12–24GB. — [Clore](https://docs.clore.ai/guides/guides_v2-de/3d-generierung/hunyuan-world-2)
- **HunyuanWorld-Voyager** (September 2025) explores a world from video and exports it to 3D. I could not confirm its license or consumer-GPU fit. — [Taibo](https://en.taibo.cn/p/25980312)

### Inferences
- For video-to-3D on a 4090, WorldMirror is the most fitting option. For single objects, TRELLIS.2 is safest because of its MIT license.

### Gaps
- I did not check whether each project's Windows install works without WSL.
- I found nothing on Hunyuan3D 3.x open weights. Some sites mention "3.5", but they look commercial or hosted.

## Which AI game mods stood out recently?

### Takeaway
Most of the recent activity is in RimWorld, where several Steam Workshop mods support Ollama. On the Skyrim side, the CHIM ecosystem (Dwemer Dynamics) has grown, and it also has a Fallout: New Vegas client. For Minecraft, Mindcraft is the active local-LLM agent framework. Mod quality varies a lot, and some mods are abandoned.

### Cited Findings
- The **Dwemer Dynamics** GitHub org maintains CHIM tooling: a launcher, a WebSocket STT plugin (currently Deepgram only), a Twitch bot, a 3D embedding visualizer, an installer, and a Fallout: New Vegas AI-NPC client. — [GitHub](https://github.com/Dwemer-Dynamics/)
- **Mindcraft** connects LLMs to Mineflayer bots that write code to perform tasks, and it supports Ollama (for example llama3 plus nomic-embed-text, and a community "Andy" model). Code execution is off by default, and the docs recommend Docker. It comes with a 2025 paper, arXiv 2504.17950. — [jimmysong summary](https://jimmysong.io/en/ai/mindcraft); official repo mindcraft-bots/mindcraft
- **RimWorld mods:** OpenRimWorldAI added Ollama in v1.0 and an "AskAPawn" feature in v1.1. — [Steam changelog](https://steamcommunity.com/sharedfiles/filedetails/changelog/3411917876?p=1). EchoColony characters drift out of persona after a few turns on local Ollama models. — [Steam discussion](https://steamcommunity.com/workshop/filedetails/discussion/3463505750/600780465871269721). RimAI Framework is "problematic" and its author is rewriting it. Local AI Social Interactions is a weekend project that its author does not plan to develop further. — [Steam](https://steamcommunity.com/sharedfiles/filedetails/comments/3413305419)

### Inferences
- All of these run on Windows. A 4090 can host an 8–14B model alongside the game, though running a game and an LLM together competes for VRAM.

### Gaps
- I found no 2026-dated standout mods. Results were mostly from 2024–2025.
- I found nothing from Nexus Mods or Reddit.

## Text-to-motion (extra)
- **HY-Motion 1.0** (Tencent, December 2025): a roughly 1B flow-matching DiT, trained on more than 3,000 hours of motion data with 400 hours of fine-tuning plus RLHF, covering over 200 motion categories. A Lite variant exists. Claims of Blender, Unity and UE support come from news aggregators only, and I found no official Blender add-on. — [arXiv 2512.23464](https://arxiv.org/abs/2512.23464v1); [HF mirror](https://huggingface.co/ZeyuLing/Motius-HYMotion-T2M-1.0-Lite)
- Gap: I found no other novel text-to-motion tools from 2026.
