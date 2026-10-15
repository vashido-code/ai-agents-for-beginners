# Niche local agent systems (self-evolving tools, desktop-observation, memory/MCP, multi-machine, GPU scheduling)

Scope note: this pass used 9 searches and no full-page fetches. Facts come from search snippets and are often from third-party directories, so star counts and dates should be checked on GitHub. Hardware fit is judged against an RTX 4090 (24GB) plus an RTX A2000 laptop on Windows; these are inferences unless marked otherwise.

## Which concrete repos/papers exist for self-improving tool-writing agents runnable locally?

### Takeaway
The strongest concrete items are research code: Yunjue Agent (Jan 2026) and Alita / Alita-G (2025). Both synthesize new tools or MCP servers when they lack a capability. Hermes Agent (NousResearch) is a more popular, hobbyist-facing option built around "skill acquisition". All three are model-agnostic in principle, but the reported results use frontier APIs.

### Cited Findings
- **Yunjue Agent (arXiv 2601.18226, Jan 2026; v2 exists):** searches its tool repository first, then synthesizes new task-specific tools when a capability is missing. The authors say they released the code, system traces and evolved tools. — [arXiv abs](https://arxiv.org/abs/2601.18226); [HTML v2](https://arxiv.org/html/2601.18226v2)
- **Alita (GitHub CharlesQ9/Alita):** "Maximal Self-Evolution". The agent creates, refines and reuses its own capabilities as MCP servers. The author says the GAIA scores were measured with no pre-initialized MCPs. — [sourcepulse summary](https://www.sourcepulse.org/projects/3794693); [repo mirror](https://gitblind.noratr.app/CharlesQ9/Alita)
- **Alita-G (arXiv 2510.23601, Oct 2025):** builds candidate MCPs from successful trajectories, abstracts them into parameterized primitives in an "MCP Box", and retrieves them by description at inference. Reports 83.03% pass@1 and 89.09% pass@3 on GAIA validation, using about 15% fewer tokens than a strong baseline. — [arXiv](https://arxiv.org/abs/2510.23601v1)
- **Hermes Agent (NousResearch, reportedly Feb 2026, MIT):** focuses on creating reusable procedures (skills) from complex tasks. The "8,700+ stars" figure comes from a secondary blog and is unverified. — [noqta blog](https://noqta.tn/en/blog/self-improving-ai-agents-autonomous-learning-2026)
- **Axonix (coe0718/axonix, Rust, created 2026-03-14, MIT):** a very small, Claude-based self-evolving agent with about 5 stars. Tool generation is not confirmed. — [ecosyste.ms](https://awesome.ecosyste.ms/projects/github.com%2Fcoe0718%2Faxonix)
- **"Self-Evolving MCP Brain" (raaaas):** an MCP server listed as self-evolving. Details are not verified. — [listing](https://www.remoteopenclaw.com/mcp/raaaas/Self-Evolving-MCP-Brain)

### Inferences
- Running these on the 4090 depends on a local OpenAI-compatible model with reliable tool calls and code generation, such as a ~30B quantized coder model. Expect results well below the published GAIA numbers.
- Alita's MCP-as-tool pattern fits Windows well, because each generated tool becomes a separate MCP server process.
- The A2000 laptop could host the tool-execution sandbox, or a small model that executes tools while the 4090 does planning.

### Gaps
- Not verified: whether the Yunjue and Alita repos run with local models out of the box, and their Windows support.
- Live-SWE-agent and similar self-modifying coding agents came up in a query but were not covered by the results.

## What novel desktop-observation-to-automation projects exist (beyond Screenpipe/ActivityWatch)?

### Takeaway
MemoryLane is the most relevant: it captures screen activity, keeps only text, and exposes it over MCP, with Windows in preview. Observer AI (local screen-watching agents) and agent-watch (macOS only) are smaller alternatives. The claim that MemoryLane proposes automations comes from one HN comment and is not confirmed by its listings.

### Cited Findings
- **MemoryLane (deusXmachina-dev/memorylane, GPL-3.0):** triggered by user activity rather than fixed intervals. A vision model writes a summary and OCR text, then the screenshot is deleted and only text is stored in SQLite. Exposed as MCP (semantic search, timeline) to Claude Desktop, Claude Code and Cursor. Supports custom OpenAI-compatible endpoints such as Ollama, with cloud as the default. Windows is listed as preview. Listings disagree on stars (70 vs 122). — [directory listing](https://enterprisedna.co/directories/mcp/deusxmachina-dev-memorylane); [mdskills](https://www.mdskills.ai/skills/memorylane)
- An HN commenter described MemoryLane as finding repeated workflows and proposing automations. This is unverified. — [hnrss](https://hnrss.org/user?id=fidorka)
- **Observer AI:** open source and privacy-first. Watches the screen, logs, reacts and notifies, and is built for local AI agents. — [Product Hunt](https://www.producthunt.com/posts/observer-ai)
- **agent-watch (different-ai):** a CLI that captures on-screen text through Accessibility APIs and OCR into local SQLite. Requires macOS 13+ on Apple Silicon, so it does **not** fit Windows. — [ecosyste.ms](https://awesome.ecosyste.ms/projects/github.com%2Fdifferent-ai%2Fagent-watch)
- For context only (excluded as mainstream): Screenpipe launched as YC S26 with the pitch "record how you work and turn that into agents". — [Launch HN](https://hn.nuxt.dev/item/49024620)

### Inferences
- For Windows plus a 4090, MemoryLane pointed at a local VLM endpoint, such as a Qwen-VL class model served by llama.cpp, is the most realistic hobbyist pipeline. A separate agent could read its MCP timeline overnight and draft automations.

### Gaps
- No Windows-native, verified "observe, then auto-generate a script" open-source project was found.

## Any novel memory/MCP-memory servers or multi-machine agent setups?

### Takeaway
Memory: doobidoo/mcp-memory-service is the most mature shared multi-agent MCP memory. Several tiny 2026 servers exist but are barely adopted. Multi-machine: llama.cpp RPC pools memory but does not add speed. prima.cpp does pipeline-parallel inference. exo is peer-to-peer but Mac/MLX-focused. Scheduling: llama-swap handles per-box VRAM swapping. No packaged tool was found that combines Wake-on-LAN with a GPU job queue.

### Cited Findings
- **mcp-memory-service (doobidoo, Apache-2.0):** shared memory across agents and runs, an agent-ID header for scoped retrieval, notifications on writes, and remote MCP. The "5ms" retrieval claim is unverified. — [glama README](https://glama.ai/mcp/servers/@doobidoo/mcp-memory-service/blob/c69b92de18b26f23b027566690bacd7035684501/README.md)
- **Tiny 2026 memory servers:** tverney/mcp-agent-memory (MIT, daemon, 3 stars); threadctx-mcp (local TypeScript, 1 star); seanmeverett/shared-memory-mcp (public by default, unsuitable for private data). — [tverney](https://enterprisedna.co/directories/mcp/tverney-mcp-agent-memory); [threadctx](https://enterprisedna.co/directories/mcp/threadctx-dev-threadctx-mcp); [shared-memory-mcp](https://enterprisedna.co/directories/mcp/seanmeverett-shared-memory-mcp)
- **Mwe-MCP:** a self-hosted shared memory pool, but the repo could not be confirmed. — [aiindigo review](https://aiindigo.com/blog/mwe-mcp-review-solving-the-memory-problem-for-multi-agent-systems-in-2026)
- **llama.cpp RPC:** pools memory across nodes. If the model already fits on one node, adding RPC workers likely slows it down. **prima.cpp** is a llama.cpp fork with pipeline parallelism that needs a fast interconnect. — [Discoverer HPC](https://hpcwithus.discoverer.bg/?p=439)
- AMD (Feb 2026) ran Kimi K2.5 on four Ryzen AI Max+ nodes through llama.cpp RPC. — [AMD guide](https://www.amd.com/de/developer/resources/technical-articles/2026/how-to-run-a-one-trillion-parameter-llm-locally-an-amd.html)
- **exo:** peer-to-peer with no master node, splits models by topology, uses MLX and tinygrad backends. — [jimmysong](https://jimmysong.io/ai/exo)
- **llama-swap (mostlygeek, MIT, single Go binary):** starts and stops model servers on demand to free VRAM, with per-model TTL and groups. Single machine only. — [betterstack guide](https://betterstack.com/community/guides/ai/llama-swap/); [pkg.go.dev](https://pkg.go.dev/github.com/mostlygeek/llama-swap)
- **GPU queues:** gpuq (Weidows, PyPI) is a single-machine, VRAM-aware priority queue with a web dashboard. gflow (runqd) is a single Linux machine scheduler with dependencies and arrays. be-lang/gpuq is a toy control-plane and agent design ("don't use for anything real"). — [gpuqu](https://pypi.org/project/gpuqu/0.1.2/); [runqd](https://pypi.org/project/runqd/); [be-lang/gpuq](https://github.com/be-lang/gpuq)
- **"Experiment-queue" skill (ARIS, "Auto-claude-code-research-in-sleep"):** an agent skill that queues experiments to run overnight. — [claudeskills](https://claudeskills.info/zh-hant/skills/wanshuiyin/Auto-claude-code-research-in-sleep/experiment-queue/)
- **Wake-on-LAN pattern:** an always-on low-power relay sends a magic packet to the GPU workstation before forwarding the request. Write-up only, not a tool. — [aiindigo](https://aiindigo.com/blog/local-ai-wake-on-lan-setup-the-pragmatic-way-to-run-heavy-llms-in-2026)
- **Hierarchical planner/executor:** pi-code-planner (m62624) is an experimental Pi extension. It runs a small local model (tested with Qwen3.6-35B-A3B) and keeps plan state on disk (v0.12.2, Jul 2026). Octo-planner (arXiv 2406.18082) uses a 3.8B on-device planner with a separate action agent. — [pi.dev](https://pi.dev/packages/pi-code-planner?name=Plan); [Octo-planner](https://papers.pytorch.kr/papers/2406.18082)

### Inferences
- For a 4090 plus A2000 (4–8GB) setup, RPC would mostly add network overhead. A better split is a 4090 inference box behind llama-swap and an A2000 laptop running a small executor or verifier model, sharing an MCP memory server.
- A hobbyist "overnight factory" can be assembled from gpuq or gflow plus llama-swap plus a WoL relay script. gflow is Linux-only, so on Windows it would need WSL2.

### Gaps
- Not covered by the searches: auditor/verifier agent repos, A2A multi-machine hobby setups, GPUStack's scheduler, and Windows support for exo or prima.cpp.
- No full pages were fetched, so all dates and star counts are from snippets.
