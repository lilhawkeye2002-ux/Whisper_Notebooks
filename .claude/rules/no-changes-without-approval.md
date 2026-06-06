---
description: Never modify project files without explicit user approval first
paths: ["**/*.ipynb", "**/*.py", "**/*.md", "**/*.json", "**/*.sh"]
---

# No Changes Without Approval

Before modifying ANY file in this project:

1. Output a complete list of every proposed change with full file content or diffs
2. State clearly: "Awaiting your approval before making changes"
3. Wait for explicit approval ("approved", "go ahead", "yes", "do it")
4. Only then apply changes

This applies to: notebooks (.ipynb), Python files (.py), markdown docs (.md), config files, scripts, and any other project file.

**Exception**: Reading, searching, cloning external repos, and installing skills globally (`~/.claude/`) do not require approval.

**Exception**: Committing and pushing to GitHub after approved changes is always required — do it automatically.
