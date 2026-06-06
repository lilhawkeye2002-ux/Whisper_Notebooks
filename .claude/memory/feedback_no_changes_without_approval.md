---
name: Feedback — no changes without explicit approval
description: Always output proposed changes list and wait for explicit approval before touching any project file
type: feedback
---

Never modify any file in the Whisper_Notebooks project without first outputting the complete proposed-changes list and receiving explicit approval.

**Why:** User has requested this explicitly in multiple sessions and has hard-stopped tasks when changes were made without prior approval. "DO NOT MAKE ANY CHANGES to the codebase until I approve them."

**How to apply:** For every task involving file modifications:
1. Output the full list of proposed changes with complete file content
2. State "Awaiting your approval before making changes"
3. Wait for "approved" / "go ahead" / "yes" / "do it"
4. Only then apply changes

This is separate from the push rule — push is always done after approved changes, automatically.
