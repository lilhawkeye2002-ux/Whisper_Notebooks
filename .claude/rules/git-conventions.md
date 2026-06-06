---
description: Git workflow and push conventions for this repo
paths: ["."]
---

# Git Conventions

## Always push after every change
Every change to this repo must be committed and pushed to GitHub before the session ends.
Never leave changes uncommitted. This is non-negotiable.
Do not ask for permission to push — just push.

## Commit message format
```
<type>: <short description>

<optional body explaining why>

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```
Types: `feat` · `fix` · `docs` · `refactor` · `chore`

## Push procedure
1. `git add <specific files>` — never `git add -A` (risks committing secrets)
2. Commit with HEREDOC for correct formatting
3. `git push origin main`
4. Confirm push succeeded — check output for remote SHA

## Remote with token
```
git remote set-url origin https://<TOKEN>@github.com/lilhawkeye2002-ux/Whisper_Notebooks.git
```
Token is in `.claude/memory/feedback_always_push.md`.

## Regression check before push
Verify no original logic was silently removed. All original variables, functions,
and transcription options must be preserved across edits.
