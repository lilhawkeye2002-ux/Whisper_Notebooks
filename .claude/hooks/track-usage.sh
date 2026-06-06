#!/usr/bin/env bash
# track-usage.sh — PostToolUse hook
# Logs every tool call to ~/.claude/coach-usage-log.jsonl
# Wired via PostToolUse in .claude/settings.local.json
# Required by /kaizen:coach for usage-based suggestions and skill adoption tracking.

LOGFILE="$HOME/.claude/coach-usage-log.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
TOOL="${CLAUDE_TOOL_NAME:-unknown}"
PROJECT="Whisper_Notebooks"

mkdir -p "$(dirname "$LOGFILE")"
printf '{"ts":"%s","tool":"%s","project":"%s"}\n' \
  "$TIMESTAMP" "$TOOL" "$PROJECT" >> "$LOGFILE"
