---
description: Python and Jupyter notebook coding conventions for this project
paths: ["**/*.ipynb", "**/*.py"]
---

# Python / Notebook Conventions

## Notebook structure
- Each logical section is labeled `# ── Phase N: Name ──────...`
- All Colab form parameters use `# @param {type:"boolean"}` or `# @param {type:"string"}`
- No `LiveFileWriter` pattern — write files directly from result data after completion
- Verbose Whisper output goes straight to stdout (no stdout redirect wrapper)

## PyTorch memory management
Per PyTorch maintainer guidance:
- `torch.cuda.empty_cache()` ONLY at major phase transitions (model device-change reload)
- NEVER call `empty_cache()` in per-file, per-chunk, or per-batch loops
- Use `del tensor; result = None` for Python-side RAM cleanup after each file
- Run `gc.collect()` once after the full transcription loop — not per iteration
- OOM recovery: `del result → gc.collect() → empty_cache()` (error-recovery state only)

## File transfer / verification
- All file copies (Drive import/export) verified with BOTH file size AND SHA-256 hash
- Use `_copy_with_verification()` — never assume a copy succeeded without verification
- Copy task does not complete until 100% verified; partial files cleaned up on failure

## Error handling
- Hard stops (`sys.exit(1)`) with crystal-clear messages for critical failures (Drive mount, etc.)
- Soft warnings for recoverable states (no speech detected, optional features failed)
- Always clean up partial/temp files in `finally` blocks

## Intentional design choices — DO NOT CHANGE
- `best_of=5` in quality mode — intentional, kept for future compatibility
- `beam_size=5` in quality mode — intentional, primary quality lever
- `"language": "ja"` in FAST_DECODE options — intentional hardcoded value
- `#"language": None` commented-out line has been removed — do not re-add it

## Regression requirement
Before any push, verify:
- All original variables present (BULK_DIR, ZIP_PATH, DEVICE, USE_MODEL, etc.)
- All original functions present (_install_libraries, _prepare_audio, _is_already_optimal_wav, _write_timestamped_txt)
- All quality-mode transcription options preserved (beam_size, best_of, temperature tuple, thresholds)
- VTT timestamp fix preserved (fix_vtt, _orig_start pattern)
- Zip logic preserved (ZIP_DEFLATED, allowZip64, arcname)
