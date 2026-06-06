# Whisper Notebooks

## Project
Google Colab Jupyter notebooks for bulk audio/video transcription and subtitle burning using OpenAI Whisper.

- **Transcription notebooks**: `Whisper_Bulk_Transcriber_AltTimestampMethod.ipynb` (primary), `Whisper_Bulk_Transcriber.ipynb`, `Whisper_Bulk_Transcriber_AltTimestampMethod_FasterWhisper.ipynb`
- **Subtitle burner**: `Cover_Video_Subtitle_Burner.ipynb` + `Cover_Video_Subtitle_Burner_cell.py`
- **Repo**: https://github.com/lilhawkeye2002-ux/Whisper_Notebooks
- **Runtime**: Google Colab (T4 GPU), `/content/` paths, `google.colab` APIs

## CRITICAL RULES — READ FIRST, EVERY SESSION

### 1. NEVER modify any file without explicit user approval
Output the complete proposed-changes list with full content first.
State: "Awaiting your approval before making changes."
Wait for explicit approval ("approved", "go ahead", "yes", "do it") before touching any file.
Exception: reading, searching, cloning external repos, installing skills globally.

### 2. ALWAYS push to GitHub after every change
Every change must be committed and pushed before the session ends.
Never leave changes uncommitted or unpushed.
Use token from `.claude/memory/feedback_always_push.md`.
Confirm push succeeded (verify remote SHA).
Do not ask for permission to push — just do it.

### 3. ALWAYS run regression check before pushing
Verify all original variables, functions, and decode options are preserved.
`best_of=5` and `beam_size=5` in quality mode are intentional.
`"language": "ja"` in FAST_DECODE is intentional.

## Architecture

```
Whisper_Bulk_Transcriber_AltTimestampMethod.ipynb  ← primary transcription notebook
  Phase 0    — constants + performance flags + Google Drive flags
  Phase 0b   — Drive mount (hard stop on failure)
  Phase 0c   — Drive audio import (SHA-256 + size verified, recursive)
  Phase 1    — directory check
  Phase 2–4  — imports, library install, ffmpeg preflight
  Phase 5    — per-file validation
  Phase 6    — Whisper model load (device guard, gc.collect on reload)
  Phase 7    — audio prep (_prepare_audio, _is_already_optimal_wav)
  Phase 8    — timestamped .txt writer (_write_timestamped_txt)
  Phase 9    — transcription options (FAST_DECODE / quality mode)
  Phase 10   — transcription loop (del result + gc.collect per PyTorch guidance)
  Phase 11   — zip outputs
  Phase 11b  — Drive export (SHA-256 verified, 120s timeout prompt)
  Phase 12   — summary

Cover_Video_Subtitle_Burner.ipynb  ← subtitle burning notebook
  ASS subtitle format, ffmpeg libass filter
  _preprocess_srt(), _clean_line(), _has_cjk(), _detect_hw_encoder()
  GPU: NVIDIA h264_nvenc hardware acceleration
  28 planned features in TODO.md | 47 rejected in WILL_NEVER_IMPLEMENT.md
```

## Key implementation notes

- `torch.cuda.empty_cache()` only at major phase transitions — never in per-file loops
- All file transfers verified by size + SHA-256 (`_copy_with_verification()`)
- `LiveFileWriter` was removed — vestigial, only mirrored stdout
- All Colab form params use `# @param {type:"boolean"}` or `# @param {type:"string"}`

## Skills installed
See `claude/` directory — engineering and productivity skill buckets.
All skills are installed globally in `~/.claude/skills/` at session start.

## Session setup (ephemeral sandbox)
This sandbox is ephemeral. On every new session:
1. Re-clone the repo: `git clone https://github.com/lilhawkeye2002-ux/Whisper_Notebooks`
2. Install skills: `cp -r claude/engineering/* ~/.claude/skills/ && cp -r claude/productivity/* ~/.claude/skills/`
3. Set git remote with token (see `.claude/memory/feedback_always_push.md`)

## Detailed docs
- `.claude/memory/` — persistent memory (user profile, project context, feedback)
- `.claude/rules/` — scoped coding and workflow rules
- `HANDOFF.md` — session handoff and feature roadmap
- `TODO.md` — 28 planned subtitle features
- `WILL_NEVER_IMPLEMENT.md` — 47 rejected features with rationale
