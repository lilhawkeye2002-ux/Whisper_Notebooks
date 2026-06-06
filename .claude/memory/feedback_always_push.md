---
name: Feedback — always push to GitHub
description: Always commit and push every change to GitHub immediately; never leave uncommitted work; token stored here
type: feedback
---

Always push to GitHub after every change using the token. Never leave changes uncommitted or unpushed.

**Why:** User has explicitly corrected this multiple times — "WHY ARE YOU NOT FUCKING PUSHING TO GITHUB with the token? ALWAYS push changes."

**How to apply:** After every approved file edit — stage specific files, commit with proper message, push. Confirm push succeeded. Do not ask for confirmation to push; just do it as part of the normal workflow.

**GitHub token:** Stored in session context — user provides it each session via chat.
Do NOT store the raw token in any committed file (GitHub Push Protection will block the push).

**Set remote (fill in token from session context):**
```bash
git remote set-url origin https://<TOKEN>@github.com/lilhawkeye2002-ux/Whisper_Notebooks.git
```
