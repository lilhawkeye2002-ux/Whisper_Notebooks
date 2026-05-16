# @title ## Cover Video Subtitle Burner
# @markdown ### Upload cover image, audio, and .srt to `/content/input/`, then run this cell.
# @markdown Outputs an MP4 with the still image, audio, and burned-in subtitles.

# ── Phase 0: Constants & Minimal Imports ─────────────────────────────────────
# Only os and sys needed here — directory check runs before any installs.

import os
import sys

INPUT_DIR = "/content/input"
TMP_SRT   = "/tmp/sanitized_subtitles.srt"
TMP_COVER = "/tmp/cover_clean.png"

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.webp'}
AUDIO_EXTS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.opus', '.wma'}
SRT_EXTS   = {'.srt'}

# ── Phase 1: Directory Check + File Detection (fail fast) ─────────────────────
# Runs instantly with no external dependencies.
# Exits immediately if files are missing or ambiguous (multiple of same type).

os.makedirs(INPUT_DIR, exist_ok=True)

_all_files = [
    f for f in os.listdir(INPUT_DIR)
    if os.path.isfile(os.path.join(INPUT_DIR, f))
]

img_files   = sorted([f for f in _all_files if os.path.splitext(f)[1].lower() in IMAGE_EXTS])
audio_files = sorted([f for f in _all_files if os.path.splitext(f)[1].lower() in AUDIO_EXTS])
srt_files   = sorted([f for f in _all_files if os.path.splitext(f)[1].lower() in SRT_EXTS])

_missing = []
if not img_files:   _missing.append("cover image  (.png / .jpg / .jpeg / .webp)")
if not audio_files: _missing.append("audio file   (.mp3 / .wav / .m4a / .aac / .flac etc.)")
if not srt_files:   _missing.append("subtitle file  (.srt)")

if _missing:
    sys.exit(
        f"\nMissing file(s) in '{INPUT_DIR}':\n" +
        "".join(f"  - {m}\n" for m in _missing) +
        "\nUpload all three files and run this cell again.\n"
    )

for _label, _found in [
    ("cover image",   img_files),
    ("audio file",    audio_files),
    ("subtitle file", srt_files),
]:
    if len(_found) > 1:
        sys.exit(
            f"[ERROR] Multiple {_label}s found — keep exactly ONE:\n" +
            "".join(f"  {f}\n" for f in _found) +
            "Remove the extras and re-run.\n"
        )

cover_path = os.path.join(INPUT_DIR, img_files[0])
audio_path = os.path.join(INPUT_DIR, audio_files[0])
srt_path   = os.path.join(INPUT_DIR, srt_files[0])

print(f"Cover : {img_files[0]}")
print(f"Audio : {audio_files[0]}")
print(f"SRT   : {srt_files[0]}")
print("Files confirmed. Loading dependencies...")

# ── Phase 2: Full Stdlib Imports ──────────────────────────────────────────────
import re
import subprocess

# ── Phase 3: Library Install ──────────────────────────────────────────────────
_pip = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q",
     "--root-user-action=ignore", "Pillow", "charset-normalizer"],
    capture_output=True, text=True
)
if _pip.returncode != 0:
    print(f"[ERROR] pip install failed:\n{_pip.stderr}")
    sys.exit(1)

from PIL import Image
from charset_normalizer import from_path as detect_encoding
print("Libraries confirmed.")

# ── Phase 4: ffmpeg + libass Pre-flight ───────────────────────────────────────
if subprocess.run(["ffmpeg", "-version"], capture_output=True).returncode != 0:
    print("ffmpeg not found — installing...")
    _apt = subprocess.run(
        ["apt", "install", "-y", "-qq", "ffmpeg", "libass9", "libass-dev"],
        capture_output=True, text=True
    )
    if _apt.returncode != 0:
        print(f"[ERROR] apt install failed:\n{_apt.stderr}")
        sys.exit(1)

_filters_out = subprocess.run(["ffmpeg", "-filters"], capture_output=True, text=True)
if "subtitles" not in (_filters_out.stdout + _filters_out.stderr):
    print("[ERROR] libass/subtitles filter unavailable in this ffmpeg build.")
    print("Run in a new cell:  !apt install -y ffmpeg libass9 libass-dev")
    sys.exit(1)

_ver_line = subprocess.run(
    ["ffmpeg", "-version"], capture_output=True, text=True
).stdout.split("\n")[0]
print(f"ffmpeg : {_ver_line}")
print("libass subtitles filter : confirmed.")

# ── Phase 4b: Hardware Acceleration Detection ─────────────────────────────────
# Probes available Colab hardware and selects the best ffmpeg video encoder.
#
# Priority order:
#   1. h264_nvenc (NVIDIA GPU)  — T4 / A100 / V100 / L4 on Colab free & Pro
#   2. libx264   (CPU fallback) — always available, used when no GPU is present
#
# The subtitle (libass) filter is CPU-only regardless of GPU availability;
# only the final H.264 encoding step is hardware-accelerated.
#
# Why three test modes instead of one:
#   ffmpeg 4.4.2 (Ubuntu 22.04 — the version Colab ships) requires an explicit
#   -rc (rate-control) mode before -cq is accepted by h264_nvenc. Without -rc,
#   the encoder defaults to CBR and rejects the quality arg. Three modes are
#   tried in order; the first that succeeds is stored for the actual encode.
#
#   Additionally, CUDA runtime libraries (libcuda.so, libnvcuvid.so) live in
#   /usr/local/cuda/lib64 and are NOT automatically on LD_LIBRARY_PATH for
#   subprocesses on Colab. Without explicit path injection, every ffmpeg NVENC
#   call silently fails with "No capable devices found" or "Cannot load nvcuda".

import os as _os

# Build a subprocess environment with CUDA library paths.
# Strategy: query ldconfig first (reflects the actual runtime linker cache),
# then fall back to known Colab path patterns for any that ldconfig missed.
_CUDA_ENV = _os.environ.copy()

_ldconf = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
_cuda_dirs = set()
for _ldline in _ldconf.stdout.splitlines():
    # Match lines for the three libraries NVENC depends on
    if any(kw in _ldline for kw in ("libcuda", "libnvcuvid", "libnvidia-encode")):
        if "=>" in _ldline:
            _lib_path = _ldline.split("=>")[-1].strip()
            _lib_dir  = _os.path.dirname(_lib_path)
            if _lib_dir and _os.path.isdir(_lib_dir):
                _cuda_dirs.add(_lib_dir)

# Add known Colab CUDA paths as additional fallback
for _p in [
    "/usr/local/cuda/lib64",
    "/usr/local/cuda-12/lib64",
    "/usr/local/cuda-12.0/lib64",
    "/usr/local/cuda-11.8/lib64",
    "/usr/lib/x86_64-linux-gnu",
]:
    if _os.path.isdir(_p):
        _cuda_dirs.add(_p)

_cuda_extra = ":".join(sorted(_cuda_dirs))
if _cuda_extra:
    _CUDA_ENV["LD_LIBRARY_PATH"] = (
        _cuda_extra + ":" + _CUDA_ENV.get("LD_LIBRARY_PATH", "")
    )
    print(f"CUDA lib paths   : {_cuda_extra}")

# NVENC RC modes tried in priority order.
# Each entry: (label, quality_flag, quality_flag_name, extra_rc_args)
#   vbr      — variable bitrate quality mode, modern default
#   vbr_hq   — high-quality VBR, highest quality but may not exist on older SDK
#   constqp  — constant QP, most compatible, widest driver support
_NVENC_RC_MODES = [
    ("vbr",     ["-rc", "vbr",     "-cq",  None, "-b:v", "0"]),
    ("vbr_hq",  ["-rc", "vbr_hq", "-cq",  None, "-b:v", "0"]),
    ("constqp", ["-rc", "constqp", "-qp",  None            ]),
]
# None placeholders above are filled with the actual quality value at encode time.


def _detect_hw_encoder() -> dict:
    info = {
        'encoder':        'libx264',
        'nvenc_rc_mode':  None,    # which RC mode succeeded (vbr/vbr_hq/constqp)
        'nvenc_rc_args':  None,    # pre-built quality args for that mode
        'gpu_name':       None,
        'gpu_mem_mb':     None,
        'reason':         'CPU — libx264 (no NVIDIA GPU detected)',
    }

    # (a) NVIDIA GPU presence
    _smi = subprocess.run(
        ["nvidia-smi",
         "--query-gpu=name,memory.total",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    )
    if _smi.returncode != 0 or not _smi.stdout.strip():
        return info

    _parts = [p.strip() for p in _smi.stdout.strip().split(",")]
    info['gpu_name']   = _parts[0]
    info['gpu_mem_mb'] = _parts[1] if len(_parts) > 1 else "unknown"

    # (b) h264_nvenc compiled into this ffmpeg build
    _enc_list = subprocess.run(
        ["ffmpeg", "-encoders"], capture_output=True, text=True
    )
    if "h264_nvenc" not in (_enc_list.stdout + _enc_list.stderr):
        info['reason'] = (
            f"CPU — libx264  [{info['gpu_name']} found but "
            f"ffmpeg has no h264_nvenc — try: !apt install -y ffmpeg]"
        )
        return info

    # (c) Try each NVENC RC mode with a 1-second 64×64 test encode.
    #     Use the CUDA-aware environment for every subprocess call.
    _last_err = ""
    for _rc_label, _rc_args_template in _NVENC_RC_MODES:
        # Fill the None quality placeholder with value 23 for the test
        _rc_test_args = [
            "23" if a is None else a for a in _rc_args_template
        ]
        _test_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=black:s=64x64:d=1:r=1",
            "-c:v", "h264_nvenc", "-preset", "fast",
            *_rc_test_args,
            "-f", "null", "-",
        ]
        _test = subprocess.run(
            _test_cmd,
            capture_output=True, text=True,
            env=_CUDA_ENV,
        )
        if _test.returncode == 0:
            # This RC mode works — store it for use in the actual encode
            info['encoder']       = 'h264_nvenc'
            info['nvenc_rc_mode'] = _rc_label
            info['nvenc_rc_args'] = _rc_args_template   # None slots filled later
            info['reason'] = (
                f"GPU — h264_nvenc/{_rc_label}  "
                f"[{info['gpu_name']}, {info['gpu_mem_mb']} MB VRAM]"
            )
            return info
        # Extract the actual diagnostic lines — NVENC / CUDA errors appear
        # in the middle of stderr; "Conversion failed!" is always the last
        # line and carries no useful information.
        _diagnostic_keywords = (
            "h264_nvenc", "nvenc", "cuda", "nvcuvid", "libnvcuvid",
            "driver", "device", "encode", "session", "version",
            "failed", "error", "cannot", "unable", "no capable",
        )
        _relevant = [
            l.strip() for l in _test.stderr.splitlines()
            if l.strip()
            and "Conversion failed" not in l
            and any(kw in l.lower() for kw in _diagnostic_keywords)
        ]
        _last_err = (
            "\n             ".join(_relevant[-6:])
            if _relevant
            else (_test.stderr.strip() or "(no stderr output)")
        )

    # All three RC modes failed — surface the actual ffmpeg error
    info['reason'] = (
        f"CPU — libx264  [{info['gpu_name']} found, h264_nvenc present, "
        f"but all NVENC RC modes failed]\n"
        f"          NVENC error: {_last_err}"
    )
    return info


_hw = _detect_hw_encoder()
print(f"Hardware encoder : {_hw['reason']}")

# ── Phase 5: Font Installation + Name Verification ───────────────────────────
# DejaVu Sans     — Latin/Greek/Cyrillic, guaranteed on Ubuntu
# Noto Sans CJK JP — Japanese/Chinese/Korean (auto-selected when SRT contains CJK)
subprocess.run(
    ["apt", "install", "-y", "-qq", "fonts-dejavu-core", "fonts-noto-cjk"],
    capture_output=True
)
subprocess.run(["fc-cache", "-fv"], capture_output=True)

_fc_list   = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
FONT_LATIN = "DejaVu Sans"
FONT_CJK   = "Noto Sans CJK JP"

if FONT_LATIN not in _fc_list:
    print(f"[WARN] '{FONT_LATIN}' not in fontconfig — subtitles may use fallback font.")
else:
    print(f"Font confirmed : {FONT_LATIN}")

if FONT_CJK not in _fc_list:
    print(f"[WARN] '{FONT_CJK}' not in fontconfig — CJK subtitles may not render.")
else:
    print(f"Font confirmed : {FONT_CJK}")

# ── Phase 6: File Validation ──────────────────────────────────────────────────

# 6a — Cover image integrity check
try:
    _img_test = Image.open(cover_path)
    _img_test.verify()
except Exception as _e:
    sys.exit(f"[ERROR] Cover image corrupt or unreadable: {_e}")

# 6b — Audio: ffprobe for duration (also validates the file is readable)
_audio_probe = subprocess.run(
    [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path,
    ],
    capture_output=True, text=True,
)
if _audio_probe.returncode != 0:
    sys.exit(
        f"[ERROR] Audio file corrupt or unsupported:\n{_audio_probe.stderr.strip()}"
    )
try:
    audio_duration_secs = float(_audio_probe.stdout.strip())
    print(f"Audio duration : {audio_duration_secs:.3f}s")
except ValueError:
    audio_duration_secs = None
    print("[WARN] Could not read audio duration — will use SRT duration.")

# 6c — SRT non-empty check
if os.path.getsize(srt_path) == 0:
    sys.exit("[ERROR] SRT file is empty.")

print("File validation passed.")

# ── Phase 7: SRT Preprocessing ────────────────────────────────────────────────
# Normalises encoding, line endings, timing separators, and strips problematic
# markup. Writes a clean UTF-8 SRT to a safe ASCII temp path, eliminating every
# class of ffmpeg filter path-escaping issue.

# 7a — Detect encoding and decode
_detected = detect_encoding(srt_path).best()
if _detected is None:
    _raw_bytes = open(srt_path, "rb").read()
    for _enc in ("utf-8-sig", "utf-8", "latin-1", "cp1252", "shift_jis"):
        try:
            _content = _raw_bytes.decode(_enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        sys.exit("[ERROR] Cannot detect SRT file encoding.")
else:
    _content = str(_detected)   # charset_normalizer strips BOM automatically

# 7b — Normalise line endings (CRLF and bare CR → LF)
_content = _content.replace("\r\n", "\n").replace("\r", "\n")

# 7c — Normalise timing separator: some exporters use HH:MM:SS.mmm not HH:MM:SS,mmm
_TIMING_PERIOD = re.compile(
    r"^(\d{2}:\d{2}:\d{2})\.(\d{3}\s*-->\s*\d{2}:\d{2}:\d{2})\.(\d{3})",
    re.MULTILINE,
)
_content = _TIMING_PERIOD.sub(r"\1,\2,\3", _content)

# 7d — Strip ASS override tags and problematic HTML from subtitle text lines.
#      Timing lines and sequence-number lines are left untouched.
#      <i>, <b>, <u> are preserved (libass handles them natively).
_IS_TIMING = re.compile(
    r"^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
)
_IS_SEQ = re.compile(r"^\d+\s*$")


def _clean_line(line: str) -> str:
    line = re.sub(r"\{[^}]*\}", "", line)                           # {\\an8} ASS tags
    line = re.sub(r"<font[^>]*>", "", line, flags=re.IGNORECASE)    # <font ...>
    line = re.sub(r"</font>",     "", line, flags=re.IGNORECASE)    # </font>
    # Remove all HTML except <i>, </i>, <b>, </b>, <u>, </u>
    line = re.sub(r"<(?!/?(?:i|b|u)>)[^>]+>", "", line)
    return line


_cleaned_lines = []
for _ln in _content.split("\n"):
    if _IS_TIMING.match(_ln.strip()) or _IS_SEQ.match(_ln.strip()):
        _cleaned_lines.append(_ln)
    else:
        _cleaned_lines.append(_clean_line(_ln))
_content = "\n".join(_cleaned_lines)

# 7e — Collapse excess blank lines (3+ consecutive blank lines → 1)
_content = re.sub(r"\n{3,}", "\n\n", _content).strip() + "\n"

# 7f — Parse last cue end time to determine SRT total duration
_END_TIME_RE = re.compile(
    r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
)


def _srt_to_secs(t: str) -> float:
    t = t.strip().replace(",", ".")
    h, m, rest = t.split(":")
    s, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


_end_times = [_srt_to_secs(m) for m in _END_TIME_RE.findall(_content)]
if not _end_times:
    sys.exit("[ERROR] No valid subtitle timing lines found in SRT file.")

srt_duration_secs = max(_end_times)
_srt_mm = int(srt_duration_secs // 60)
_srt_ss = int(srt_duration_secs % 60)
print(f"SRT duration : {srt_duration_secs:.3f}s  ({_srt_mm:02d}:{_srt_ss:02d})")

# 7g — Write sanitized SRT to safe ASCII temp path
with open(TMP_SRT, "w", encoding="utf-8") as _f:
    _f.write(_content)
print(f"SRT sanitized → {TMP_SRT}")

# ── Phase 8: Image Preprocessing ─────────────────────────────────────────────
# Converts to RGB (libx264 cannot accept RGBA/palette modes).
# Composites transparent images onto a black background.
# Enforces even pixel dimensions (libx264 hard requirement).

img = Image.open(cover_path)

if img.mode in ("RGBA", "LA"):
    _bg = Image.new("RGB", img.size, (0, 0, 0))
    _bg.paste(img, mask=img.split()[-1])
    img = _bg
elif img.mode in ("PA", "P"):
    _rgba = img.convert("RGBA")
    _bg = Image.new("RGB", img.size, (0, 0, 0))
    _bg.paste(_rgba, mask=_rgba.split()[-1])
    img = _bg
elif img.mode != "RGB":
    img = img.convert("RGB")

w, h = img.size
w = w if w % 2 == 0 else w - 1
h = h if h % 2 == 0 else h - 1
if (w, h) != img.size:
    img = img.crop((0, 0, w, h))

img_width, img_height = w, h
img.save(TMP_COVER, "PNG")
print(f"Cover preprocessed : {img_width}x{img_height} → {TMP_COVER}")

# ── Phase 9: Duration Resolution + Output Path ────────────────────────────────

video_duration = srt_duration_secs

if audio_duration_secs is not None:
    if audio_duration_secs > srt_duration_secs:
        video_duration = audio_duration_secs
        print(
            f"[INFO] Audio ({audio_duration_secs:.1f}s) longer than SRT "
            f"({srt_duration_secs:.1f}s) — extending video to audio length."
        )
    elif audio_duration_secs < srt_duration_secs - 1.0:
        print(
            f"[INFO] Audio ({audio_duration_secs:.1f}s) shorter than SRT "
            f"({srt_duration_secs:.1f}s) — silence will pad the end."
        )


def _safe_stem(path: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    safe = "".join(
        c if c.isascii() and (c.isalnum() or c in "-_. ") else "_"
        for c in stem
    ).strip("_")
    return safe[:80] or "output"


OUTPUT_PATH = f"/content/{_safe_stem(srt_path)}.mp4"
print(f"Output duration : {video_duration:.3f}s")
print(f"Output path     : {OUTPUT_PATH}")

# ── Phase 10: User Style Parameters ──────────────────────────────────────────
# @markdown ---
# @markdown ## Output Settings
output_resolution = "Original"  # @param ["Original", "1920x1080", "1280x720", "854x480"]
video_crf         = 23          # @param {type:"slider", min:18, max:35, step:1}
video_quality     = "medium"    # @param ["fast", "medium", "slow"]

# @markdown ## Subtitle Style
font_size    = 28       # @param {type:"slider", min:12, max:72, step:2}
font_color   = "white"  # @param ["white", "yellow", "cyan", "black", "green"]
outline_size = 2        # @param {type:"slider", min:0, max:5, step:1}
shadow_size  = 1        # @param {type:"slider", min:0, max:3, step:1}
position     = "bottom" # @param ["bottom", "top"]
margin_v     = 25       # @param {type:"slider", min:0, max:150, step:5}
margin_lr    = 40       # @param {type:"slider", min:0, max:200, step:10}

# ASS color format: &HAABBGGRR& — AA=00 means fully opaque
_COLOR_MAP = {
    "white":  "&H00FFFFFF&",
    "yellow": "&H0000FFFF&",   # BGR: 00-FF-FF → RGB(255,255,0)
    "cyan":   "&H00FFFF00&",   # BGR: FF-FF-00 → RGB(0,255,255)
    "black":  "&H00000000&",
    "green":  "&H0000FF00&",   # BGR: 00-FF-00 → RGB(0,255,0)
}
_primary_colour = _COLOR_MAP[font_color]
_outline_colour = "&H00000000&"            # black outline always
_alignment      = 2 if position == "bottom" else 8  # 2=centre-bottom, 8=centre-top

# Output dimensions (enforce even numbers for libx264)
if output_resolution == "Original":
    _out_w, _out_h = img_width, img_height
else:
    _out_w, _out_h = map(int, output_resolution.split("x"))

_out_w = _out_w if _out_w % 2 == 0 else _out_w - 1
_out_h = _out_h if _out_h % 2 == 0 else _out_h - 1


def _has_cjk(text: str) -> bool:
    for ch in text:
        cp = ord(ch)
        if (0x3000 <= cp <= 0x9FFF
                or 0xF900 <= cp <= 0xFAFF
                or 0x20000 <= cp <= 0x2FA1F):
            return True
    return False


with open(TMP_SRT, encoding="utf-8") as _f:
    _srt_text = _f.read()

_font_name = FONT_CJK if _has_cjk(_srt_text) else FONT_LATIN
print(f"Font selected : {_font_name}")

# ── Phase 11: ffmpeg Command Build + Execute ──────────────────────────────────

# force_style: PlayResX/Y set the coordinate space so MarginV/L/R are in actual
# output pixels. WrapStyle=0 enables smart word-wrap for long subtitle lines.
_force_style = (
    f"PlayResX={_out_w},"
    f"PlayResY={_out_h},"
    f"FontName={_font_name},"
    f"FontSize={font_size},"
    f"PrimaryColour={_primary_colour},"
    f"OutlineColour={_outline_colour},"
    f"BorderStyle=1,"
    f"Outline={outline_size},"
    f"Shadow={shadow_size},"
    f"WrapStyle=0,"
    f"Alignment={_alignment},"
    f"MarginV={margin_v},"
    f"MarginL={margin_lr},"
    f"MarginR={margin_lr}"
)

# TMP_SRT = /tmp/sanitized_subtitles.srt — no colons, spaces, or special chars.
# charenc=UTF-8 overrides any libass internal encoding detection attempt.
_subtitle_filter = (
    f"subtitles='{TMP_SRT}'"
    f":charenc=UTF-8"
    f":force_style='{_force_style}'"
)

# Scale filter — two passes guarantee even dimensions through all code paths:
# Pass 1: fit image within target dimensions (letterbox/pillarbox if needed)
# Pass 2: trunc(x/2)*2 forces even width and height (libx264 hard requirement)
if output_resolution == "Original":
    _scale_filter = "scale=trunc(iw/2)*2:trunc(ih/2)*2"
else:
    _scale_filter = (
        f"scale={_out_w}:{_out_h}:force_original_aspect_ratio=decrease,"
        f"scale=trunc(iw/2)*2:trunc(ih/2)*2,"
        f"pad={_out_w}:{_out_h}:(ow-iw)/2:(oh-ih)/2:black"
    )

_vf = f"{_scale_filter},format=yuv420p,{_subtitle_filter}"


def _build_cmd(encoder: str) -> list:
    """Return the complete ffmpeg command for the given encoder ('h264_nvenc' or 'libx264')."""
    if encoder == 'h264_nvenc':
        # Fill the None placeholder in the stored RC args with the actual CRF value.
        # The None slot is the quality argument (-cq or -qp depending on RC mode).
        _rc_args = [
            str(video_crf) if a is None else a
            for a in _hw['nvenc_rc_args']
        ]
        _enc_args = [
            "-c:v", "h264_nvenc",
            *_rc_args,
            "-preset", video_quality,   # fast/medium/slow map directly to nvenc presets
        ]
    else:
        _enc_args = [
            "-c:v", "libx264",
            "-crf", str(video_crf),
            "-preset", video_quality,
        ]
    return [
        "ffmpeg", "-y",
        # Image input at 1 fps — H.264 encodes repeated identical frames as
        # near-zero-size P-frames, making long static-image videos encode fast.
        "-framerate", "1", "-loop", "1", "-i", TMP_COVER,
        # Audio input — path may contain any Unicode/special chars; safe in list mode.
        "-i", audio_path,
        # Video filter chain: scale → even-dims → yuv420p → burned subtitles
        "-vf", _vf,
        # Audio filters:
        #   asetpts=PTS-STARTPTS  normalises M4A/AAC ELST edit-list offset to t=0,
        #                         keeping subtitle timings aligned with speech.
        #   apad                  pads with silence if audio ends before -t duration.
        "-af", "asetpts=PTS-STARTPTS,apad",
        # Output at standard 25 fps (interpolated from 1 fps input)
        "-r", "25",
        *_enc_args,
        # Explicit stereo AAC — avoids channel-layout warnings on some M4A inputs
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        # Required for Apple / QuickTime / browser compatibility
        "-pix_fmt", "yuv420p",
        # Hard output duration: prevents infinite loop from -loop 1
        "-t", str(video_duration),
        # Move moov atom to front of file (enables progressive streaming)
        "-movflags", "+faststart",
        OUTPUT_PATH,
    ]


def _run_ffmpeg(cmd: list) -> tuple:
    """Run ffmpeg with CUDA-aware environment, stream progress, return (returncode, last_lines)."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=_CUDA_ENV,    # ensures libcuda.so / libnvcuvid.so are discoverable
    )
    last_lines = []
    for line in proc.stdout:
        line = line.rstrip()
        if line.startswith("frame=") or line.startswith("size="):
            print(f"\r{line}", end="", flush=True)
        elif line:
            last_lines.append(line)
            if len(last_lines) > 30:
                last_lines.pop(0)
    proc.wait()
    print()
    return proc.returncode, last_lines


_mm = int(video_duration // 60)
_ss = int(video_duration % 60)
_enc_label = "NVENC CQ" if _hw['encoder'] == 'h264_nvenc' else "x264 CRF"
print(
    f"\nRendering {_mm:02d}:{_ss:02d} at {_out_w}x{_out_h} | "
    f"{_enc_label} {video_crf} | preset={video_quality} | "
    f"encoder={_hw['encoder']} | font={_font_name}\n"
)

_active_encoder = _hw['encoder']
_returncode, _last_lines = _run_ffmpeg(_build_cmd(_active_encoder))

# ── Seamless NVENC → CPU fallback ────────────────────────────────────────────
# If NVENC failed during the real encode (rare: test passed but driver stalled),
# automatically rebuild and retry the full command with libx264 on CPU.
_nvenc_fail_markers = (
    "nvenc", "No capable devices", "Cannot load", "CUDA_ERROR",
    "nvcuvid", "Encoder not found",
)
if _returncode != 0 and _active_encoder == 'h264_nvenc':
    _tail_lower = "\n".join(_last_lines).lower()
    if any(m.lower() in _tail_lower for m in _nvenc_fail_markers):
        print("[WARN] NVENC encoder failed — seamlessly retrying with CPU libx264...")
        _active_encoder = 'libx264'
        _returncode, _last_lines = _run_ffmpeg(_build_cmd('libx264'))

if _returncode != 0:
    _tail = "\n".join(_last_lines)
    print(f"[ERROR] ffmpeg exited with code {_returncode}")
    print(f"Last output:\n{_tail}")
    if "Invalid option" in _tail or "Unknown encoder" in _tail:
        print("\nHint: encoder unavailable — run:  !apt install -y ffmpeg")
    elif "No such file" in _tail:
        print("\nHint: input file not found — check /content/input/ contents.")
    elif "subtitles" in _tail.lower() or "ass" in _tail.lower():
        print("\nHint: subtitle filter error — inspect /tmp/sanitized_subtitles.srt")
        print("      Likely cause: libass not compiled into this ffmpeg build.")
    elif "Invalid data" in _tail or "moov atom" in _tail:
        print("\nHint: audio file may be corrupt or in an unsupported format.")
    elif "not divisible" in _tail:
        print("\nHint: dimension parity error — please report this bug.")
    sys.exit(1)

# ── Phase 12: Output Verification + Download Prompt ──────────────────────────

if not os.path.exists(OUTPUT_PATH) or os.path.getsize(OUTPUT_PATH) == 0:
    sys.exit("[ERROR] Output file was not created or is empty.")

_size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)

_verify = subprocess.run(
    [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=codec_type,codec_name,width,height,duration",
        "-of", "default=noprint_wrappers=1",
        OUTPUT_PATH,
    ],
    capture_output=True, text=True,
)

print(f"\n✓  {OUTPUT_PATH}  ({_size_mb:.2f} MB)")
print(_verify.stdout.strip())
print()
print("Download: right-click the file in the Files panel (📁 left sidebar) → Download")
print("⚠️  Download before closing the session — /content/ is erased on disconnect.")
