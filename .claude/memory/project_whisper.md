---
name: Whisper Notebooks project
description: Google Colab Jupyter notebooks for Whisper transcription and ASS subtitle burning
type: project
---

Repo: https://github.com/lilhawkeye2002-ux/Whisper_Notebooks (main branch)

Primary notebook: Whisper_Bulk_Transcriber_AltTimestampMethod.ipynb
Subtitle notebook: Cover_Video_Subtitle_Burner.ipynb + Cover_Video_Subtitle_Burner_cell.py
FasterWhisper variant: Whisper_Bulk_Transcriber_AltTimestampMethod_FasterWhisper.ipynb

**Why:** Active multi-session development. Project has 28 planned subtitle features (TODO.md) and 47 rejected ones (WILL_NEVER_IMPLEMENT.md). Each session uses HANDOFF.md to resume context.

**How to apply:** Read claude.md, HANDOFF.md, and TODO.md at session start. Check git log for most recent changes. Re-install skills from claude/ directory.

**Session setup:**
```bash
git clone https://github.com/lilhawkeye2002-ux/Whisper_Notebooks /home/vercel-sandbox/Whisper_Notebooks
cp -r /home/vercel-sandbox/Whisper_Notebooks/claude/engineering/* ~/.claude/skills/
cp -r /home/vercel-sandbox/Whisper_Notebooks/claude/productivity/* ~/.claude/skills/
git remote set-url origin https://<TOKEN>@github.com/lilhawkeye2002-ux/Whisper_Notebooks.git
```
