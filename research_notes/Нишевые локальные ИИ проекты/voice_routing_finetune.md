# Niche local voice, routing and fine-tuning projects (2025–2026)

Target hardware: an RTX 4090 desktop (24 GB) and an RTX A2000 laptop (4–8 GB), both on Windows. Research was done 2026-10-15 using about 10 web searches. Most performance figures come from the projects themselves or from third-party blogs, so they are flagged as unverified. I did not open the GitHub repos or check licenses directly.

## What new full-duplex / speech-to-speech open models exist and run on 24GB?

### Takeaway
NVIDIA PersonaPlex-7B-v1 (Jan 2026) is the most practical new full-duplex model for a 4090. It is built on Moshi and fits in 16–24 GB. NemotronLabs VoiceChat (full-duplex with tool calling), KRAFTON Raon-SpeechChat and Kyutai's MoshiRAG are newer research-grade options. None of them is realistic on the A2000 laptop. On the laptop, a cascaded pipeline with barge-in (skadoosh, or the brainwagon design) is the way to stay under one second.

### Cited Findings
1. **NVIDIA PersonaPlex-7B-v1**, released 2026-01-20. It is a 7B full-duplex model on the Moshi architecture that listens and speaks at the same time, and the persona and voice can be set by prompt. The weights are at `nvidia/personaplex-7b-v1` (gated, about 15 GB). VRAM needs differ by source: one guide says 16 GB minimum, another says NVIDIA recommends 24 GB, and I did not see the official card. There is also a one-click Pinokio installer, which helps on Windows. **Fit:** 4090 yes; A2000 no. — [comfyui-wiki](https://comfyui-wiki.com/en/news/2026-01-20-nvidia-personaplex-7b-v1-release), [setup guide](https://themenonlab.blog/blog/nvidia-personaplex-full-duplex-voice-ai-how-to-guide), [Pinokio](https://pinokio.co/apps/github-com-pierrunoyt-personaplex-pinokio), [ai-tldr (MIT code / NVIDIA Open Model weights, secondary source)](https://ai-tldr.dev/releases/nvidia-personaplex/)
2. **NemotronLabs VoiceChat (NVIDIA, arXiv 2026).** It is unusual because it is full-duplex speech-to-speech with tool calling, and tool calls go out on a separate output channel. A collaborator's post claims about 450 ms latency, which I could not verify. I could not confirm the size, release status or the arXiv ID (2609.21967 looks odd), so check before using it. — [arXiv](https://arxiv.org/pdf/2609.21967)
3. **KRAFTON Raon-Speech / Raon-SpeechChat.** A 9B backbone with a separate full-duplex track, uncommon because it comes from a game studio. The only source is a directory entry, and I did not check VRAM; a 9B model probably needs quantization to fit in 24 GB. — [voiceaispace](https://www.voiceaispace.com/knowledge/repo/72ae7d67-6d39-4ffc-9fde-e229985ba73f)
4. **Kyutai MoshiRAG (2026).** It adds asynchronous knowledge retrieval to a full-duplex model, so the model keeps talking while the lookup runs. Moshi itself (7B) already runs on a 4090. — [Kyutai blog](https://kyutai.org/blog/), [moshi repo](https://gittrend.io/repo/kyutai-labs/moshi)
5. **NeMo Duplex S2S (2025)** describes itself as the first openly available duplex speech-to-speech model with training code. It suits anyone who wants to train or fine-tune a duplex model on the 4090. — [arXiv 2505.15670](https://arxiv.org/html/2505.15670v3)
6. **Sommelier (ACL 2026 industry track)** is an open pipeline for preparing multi-turn audio data to train full-duplex models, for example to build a Russian duplex dataset. — [ACL](https://preview.aclanthology.org/ingest-acl/2026.acl-industry.18/)
7. **skadoosh (Rust crate, 2026).** A fully local cascaded pipeline (VAD, STT, streaming LLM, TTS) that claims under 150 ms from end of speech to first audio "on capable hardware" (unverified), and stops speaking immediately when interrupted. It uses mainstream parts internally; the unusual part is the Rust orchestration. **Fit:** both machines, using a small LLM on the A2000. — [docs.rs](https://docs.rs/crate/skadoosh/0.2.0)
8. **brainwagon "Personal Alexa" (blog, 2026-09-04).** Barge-in works by comparing the microphone signal with the speaker output from about 100 ms earlier, a home-made form of echo cancellation. The author says the roughly 0.6 s end-to-first-audio figure was added up from two halves measured separately, not timed end to end. It is a good reference design. — [brainwagon](https://brainwagon.org/blog/2026-09-04-building-a-personal-alexa-using-localhost)

## What clever routing/dispatcher model projects exist?

### Takeaway
**Arch-Router-1.5B** (Katanemo, June 2025) is still the standout small router. Instead of scoring models on benchmarks, you describe routes in plain language ("code editing → model X"). A GGUF version exists, so it runs on the A2000. I found no new 2026 router model that clearly beats it, which is a gap in this research.

### Cited Findings
9. **Arch-Router-1.5B** maps a request to a domain/action pair that you define, and you can add new models without retraining. The authors report it beats proprietary LLMs by 7.71% on their own benchmark (self-reported). It sits inside the Arch proxy (Rust, now archgw/plano), and community GGUF builds exist. **Fit:** easily on the A2000 laptop as a local dispatcher in front of a 4090 "big brain". — [HF](https://huggingface.co/katanemo/Arch-Router-1.5B), [arXiv 2506.16655](https://arxiv.org/html/2506.16655v1), [Show HN](https://hn.svelte.dev/item/44436031), [GGUF](https://huggingface.co/Mungert/Arch-Router-1.5B-GGUF/blob/main/README.md)
- Not found: 2026 successors (for example RouteLLM forks or newer intent classifiers). Searches only returned Arch-Router material from 2025.

## What unusual hobbyist Unsloth projects stood out?

### Takeaway
I found no specific viral hobbyist project in these sources. What can be checked: Unsloth fine-tunes TTS models (Sesame CSM 1B, Orpheus 3B) about 1.5x faster with half the memory, and there is now a no-code **Unsloth Studio** (beta 2026-03-17) with a Model Arena. GRPO for TTS was not documented anywhere I looked.

### Cited Findings
10. **Unsloth TTS fine-tuning (CSM-1B, Orpheus-3B).** Training data is audio plus transcript. Starting from Orpheus-ft gives better voice consistency than base CSM, and CSM needs audio context for each speaker. Some outputs can only be saved as safetensors and are not llama.cpp-compatible. **Fit:** training on the 4090 is easy, and the A2000 may be able to QLoRA-train CSM-1B. A possible idea is a cloned voice for your own "computer", including Russian; Russian quality is untested. — [Unsloth docs](https://unsloth.ai/docs/basics/text-to-speech-tts-fine-tuning), [r/LocalLLaMA announcement](https://redlib.ssps.io/r/LocalLLaMA/comments/1kndp9f/tts_finetuning_now_in_unsloth)
11. **Unsloth Studio (beta 2026-03-17).** A local no-code web UI whose Model Arena compares a fine-tune side by side with its base model. A guide says the latest version is v0.1.512-beta (2026-07-29). Unsloth's VRAM minimums for QLoRA: 3B needs about 3.5 GB and 8B about 6 GB, so the A2000 can handle small models. — [yuv.ai](https://yuv.ai/blog/unsloth-studio-local-training), [pinggy guide](https://pinggy.io/blog/finetune_and_selfhost_llms_locally_with_unsloth/)

## Extra areas: Russian STT/TTS, JARVIS dashboards, phone models

### Takeaway
For Russian, the most notable work is **GigaAM v3** (with gigastt, a Rust server, and GGUF builds) and **T-one** (streaming ASR for telephony), plus **ESpeech** (Russian F5-TTS fine-tunes) and the **Balalaika** dataset. In the JARVIS-dashboard space, the unusual projects are vierisid/jarvis (an ambient "pebble" that follows the cursor) and openclaw-jarvis-ui (a 3D state orb).

### Cited Findings
12. **gigastt (GigaAM v3 local server, Rust).** MIT code and MIT weights according to its README. It runs as a server, can be embedded in Rust, or built as an Android binary. Its own table (self-reported) gives 3.55% WER for the RNN-T head against Vosk's 2.97% and whisper-large-v3's 15.26% on clean speech. GigaAM v3 GGUFs (cstr/gigaam-v3-GGUF) also exist, and the e2e variants output punctuation. **Fit:** both machines and CPU. — [GitHub](https://github.com/ekhodzitsky/gigastt), [SubtitleEdit PR](https://github.com/SubtitleEdit/subtitleedit/pull/13063)
13. **T-one (T-Software).** Streaming Conformer ASR for Russian telephony, with its own phrase-boundary detector that also helps with turn-taking. The vendor's benchmarks put it ahead of GigaAM v2 and Vosk on telephone audio. **Fit:** both machines. — [HF](https://huggingface.co/t-tech/T-one)
14. **ESpeech TTS** are Russian F5-TTS fine-tunes (Apache-2.0 on one card) that use ruaccent for stress marks. The base model is excluded from this list, but these Russian fine-tunes are niche. — [HF](https://huggingface.co/ESpeech/ESpeech-TTS-1_SFT-256K/blob/main/README.md)
15. **Balalaika dataset** (arXiv 2507.13563): more than 2,000 hours of studio-quality Russian speech with stress and punctuation marks, non-commercial license. Useful material for a Russian Unsloth TTS fine-tune. **Vosk-TTS** (VITS) is a lightweight alternative with 5 Russian voices. — [arXiv](https://arxiv.org/html/2507.13563v1), [vosk-tts](https://pypi.org/project/vosk-tts)
16. **vierisid/jarvis**: a background daemon with a dashboard at localhost:3142 and an ambient "pebble" that follows the cursor. **jincocodev/openclaw-jarvis-ui**: a HUD with a 3D orb showing thinking, responding and idle states. Both are lightly documented; check repo activity before relying on them. — [jarvis](https://github.com/vierisid/jarvis), [openclaw-jarvis-ui](https://github.com/jincocodev/openclaw-jarvis-ui)
17. **Phone models.** No standout distillation project turned up. The 2026 consensus is 1–4B models at Q4 through llama.cpp on Android (prebuilt `llama-android` AAR; KMP wrapper `dev.deviceai:llm` from March 2026), with memory bandwidth (50–90 GB/s) as the bottleneck. Speed claims vary between sources. — [Edge AI Vision](https://www.edge-ai-vision.com/?p=56644), [klibs](https://klibs.io/package/dev.deviceai/llm)

- Not found: a 2026 DIY "Star Trek computer" covering a whole house, beyond the brainwagon post; and hobbyist GRPO projects.
