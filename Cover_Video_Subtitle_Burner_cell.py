# Cover_Video_Subtitle_Burner_cell.py
# Standalone copy of the main encoding cell from Cover_Video_Subtitle_Burner.ipynb
# Kept in sync with the notebook. Paste into a Colab code cell to run.
# Notebook: https://colab.research.google.com/github/lilhawkeye2002-ux/Whisper_Notebooks/blob/main/Cover_Video_Subtitle_Burner.ipynb

# @title ## Cover Video Subtitle Burner — Batch Mode
# @markdown ### Upload one cover image + matching audio/SRT pairs to `/content/input/`, then run this cell.
# @markdown Each audio file is matched to its SRT by filename. One MP4 is produced per pair.

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

# ── Phase 1: Directory Check + File Detection ─────────────────────────────────
# Exactly one cover image required.
# Multiple audio and SRT files are accepted — each audio is matched to its SRT.

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
        "\nUpload all required files and run this cell again.\n"
    )

if len(img_files) > 1:
    sys.exit(
        "[ERROR] Multiple cover images found — keep exactly ONE:\n" +
        "".join(f"  {f}\n" for f in img_files) +
        "Remove the extras and re-run.\n"
    )

cover_path = os.path.join(INPUT_DIR, img_files[0])
print(f"Cover : {img_files[0]}")
print(f"Audio files found : {len(audio_files)}")
for _af in audio_files:
    print(f"  {_af}")
print(f"SRT files found   : {len(srt_files)}")
for _sf in srt_files:
    print(f"  {_sf}")

# ── Phase 1b: Audio ↔ SRT Pair Matching ──────────────────────────────────────
# Match each audio file to its SRT by stem name.
# Priority:
#   1. Exact stem match:        Track1.wav  →  Track1.srt
#   2. Underscore-prefix match: Track1.wav  →  Track1_EN.srt  (or _JA, _01, etc.)


def _find_srt_match(audio_stem, srt_list):
    # 1. Exact match
    for s in srt_list:
        if os.path.splitext(s)[0] == audio_stem:
            return s
    # 2. Underscore-prefix match — warn if ambiguous (e.g. Track1_EN.srt + Track1_JA.srt)
    candidates = [s for s in srt_list
                  if os.path.splitext(s)[0].startswith(audio_stem + "_")]
    if len(candidates) > 1:
        print(f"  [WARN] Multiple SRT matches for '{audio_stem}': "
              f"{', '.join(candidates)} — using {candidates[0]}")
    return candidates[0] if candidates else None


pairs = []           # list of (audio_path, srt_path)
unmatched_audio = []
print()
for _af in audio_files:
    _audio_stem = os.path.splitext(_af)[0]
    _matched_srt = _find_srt_match(_audio_stem, srt_files)
    if _matched_srt:
        pairs.append((
            os.path.join(INPUT_DIR, _af),
            os.path.join(INPUT_DIR, _matched_srt),
        ))
        print(f"  Matched : {_af}  →  {_matched_srt}")
    else:
        unmatched_audio.append(_af)

if unmatched_audio:
    print(f"\n[WARN] No SRT match found for:")
    for _u in unmatched_audio:
        print(f"  {_u}")
    print("These audio files will be skipped.\n")

if not pairs:
    sys.exit(
        "[ERROR] No audio/SRT pairs could be matched.\n"
        "Ensure each audio file has a matching SRT with the same base name\n"
        "(e.g. 'Track1.wav' pairs with 'Track1.srt' or 'Track1_EN.srt').\n"
    )

print(f"\n{len(pairs)} pair(s) matched. Loading dependencies...")

# ── Phase 2: Full Stdlib Imports ──────────────────────────────────────────────
import re
import shutil
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
_CUDA_ENV = _os.environ.copy()

_ldconf = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
_cuda_dirs = set()
for _ldline in _ldconf.stdout.splitlines():
    if any(kw in _ldline for kw in ("libcuda", "libnvcuvid", "libnvidia-encode")):
        if "=>" in _ldline:
            _lib_path = _ldline.split("=>")[-1].strip()
            _lib_dir  = _os.path.dirname(_lib_path)
            if _lib_dir and _os.path.isdir(_lib_dir):
                _cuda_dirs.add(_lib_dir)

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

_NVENC_RC_MODES = [
    ("vbr",     ["-rc", "vbr",     "-cq",  None, "-b:v", "0"]),
    ("vbr_hq",  ["-rc", "vbr_hq", "-cq",  None, "-b:v", "0"]),
    ("constqp", ["-rc", "constqp", "-qp",  None            ]),
]


def _detect_hw_encoder():
    info = {
        'encoder':        'libx264',
        'nvenc_rc_mode':  None,
        'nvenc_rc_args':  None,
        'gpu_name':       None,
        'gpu_mem_mb':     None,
        'reason':         'CPU — libx264 (no NVIDIA GPU detected)',
    }
    _smi = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
        capture_output=True, text=True,
    )
    if _smi.returncode != 0 or not _smi.stdout.strip():
        return info
    _parts = [p.strip() for p in _smi.stdout.strip().split(",")]
    info['gpu_name']   = _parts[0]
    info['gpu_mem_mb'] = _parts[1] if len(_parts) > 1 else "unknown"
    _enc_list = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True)
    if "h264_nvenc" not in (_enc_list.stdout + _enc_list.stderr):
        info['reason'] = (
            f"CPU — libx264  [{info['gpu_name']} found but "
            f"ffmpeg has no h264_nvenc — try: !apt install -y ffmpeg]"
        )
        return info
    _last_err = ""
    for _rc_label, _rc_args_template in _NVENC_RC_MODES:
        _rc_test_args = ["23" if a is None else a for a in _rc_args_template]
        _test_cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=black:s=64x64:d=1:r=1",
            "-c:v", "h264_nvenc", "-preset", "fast",
            *_rc_test_args,
            "-f", "null", "-",
        ]
        _test = subprocess.run(_test_cmd, capture_output=True, text=True, env=_CUDA_ENV)
        if _test.returncode == 0:
            info['encoder']       = 'h264_nvenc'
            info['nvenc_rc_mode'] = _rc_label
            info['nvenc_rc_args'] = _rc_args_template
            info['reason'] = (
                f"GPU — h264_nvenc/{_rc_label}  "
                f"[{info['gpu_name']}, {info['gpu_mem_mb']} MB VRAM]"
            )
            return info
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
    info['reason'] = (
        f"CPU — libx264  [{info['gpu_name']} found, h264_nvenc present, "
        f"but all NVENC RC modes failed]\n"
        f"          NVENC error: {_last_err}"
    )
    return info


_hw = _detect_hw_encoder()
print(f"Hardware encoder : {_hw['reason']}")

# ── Phase 5: Font Installation + Name Verification ───────────────────────────
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

# ── Phase 6a: Cover Image Validation + Preprocessing ─────────────────────────
try:
    _img_test = Image.open(cover_path)
    _img_test.verify()
except Exception as _e:
    sys.exit(f"[ERROR] Cover image corrupt or unreadable: {_e}")

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
if w < 2 or h < 2:
    sys.exit(
        f"[ERROR] Cover image too small after even-dimension enforcement: {w}x{h}. "
        f"Minimum supported size is 2x2 pixels."
    )
if (w, h) != img.size:
    img = img.crop((0, 0, w, h))

img_width, img_height = w, h
img.save(TMP_COVER, "PNG")
print(f"Cover preprocessed : {img_width}x{img_height} → {TMP_COVER}")

# ── Phase 7: SRT Helper Functions ────────────────────────────────────────────

_END_TIME_RE = re.compile(
    r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
)
_IS_TIMING = re.compile(
    r"^\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
)
_IS_SEQ = re.compile(r"^\d+\s*$")
_TIMING_PERIOD = re.compile(
    r"^(\d{2}:\d{2}:\d{2})\.(\d{3}\s*-->\s*\d{2}:\d{2}:\d{2})\.(\d{3})",
    re.MULTILINE,
)


def _srt_to_secs(t):
    t = t.strip().replace(",", ".")
    h, m, rest = t.split(":")
    s, ms = rest.split(".")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def _clean_line(line):
    line = re.sub(r"\{[^}]*\}", "", line)
    line = re.sub(r"<font[^>]*>", "", line, flags=re.IGNORECASE)
    line = re.sub(r"</font>",     "", line, flags=re.IGNORECASE)
    line = re.sub(r"<(?!/?(?:i|b|u)>)[^>]+>", "", line)
    return line


def _preprocess_srt(srt_path):
    """Sanitize SRT file → TMP_SRT (UTF-8, clean markup). Returns SRT duration in seconds."""
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
            raise RuntimeError("Cannot detect SRT file encoding.")
    else:
        _content = str(_detected)

    _content = _content.replace("\r\n", "\n").replace("\r", "\n")
    _content = _TIMING_PERIOD.sub(r"\1,\2,\3", _content)

    _cleaned_lines = []
    for _ln in _content.split("\n"):
        if _IS_TIMING.match(_ln.strip()) or _IS_SEQ.match(_ln.strip()):
            _cleaned_lines.append(_ln)
        else:
            _cleaned_lines.append(_clean_line(_ln))
    _content = "\n".join(_cleaned_lines)
    _content = re.sub(r"\n{3,}", "\n\n", _content).strip() + "\n"

    _end_times = [_srt_to_secs(m) for m in _END_TIME_RE.findall(_content)]
    if not _end_times:
        raise RuntimeError("No valid subtitle timing lines found in SRT file.")

    with open(TMP_SRT, "w", encoding="utf-8") as _f:
        _f.write(_content)
    return max(_end_times)


def _has_cjk(text):
    for ch in text:
        cp = ord(ch)
        if (0x3000 <= cp <= 0x9FFF
                or 0xF900 <= cp <= 0xFAFF
                or 0xFF00 <= cp <= 0xFFEF    # halfwidth/fullwidth forms incl. half-width katakana
                or 0x20000 <= cp <= 0x2FA1F):
            return True
    return False


# ── Phase 10: User Style Parameters ──────────────────────────────────────────
# @markdown ---
# @markdown ## Output Settings
output_resolution = "1280x720"  # @param ["Original", "1920x1080", "1280x720", "854x480"]
video_crf         = 23          # @param {type:"slider", min:18, max:35, step:1}
video_quality     = "fast"      # @param ["fast", "medium", "slow"]

# @markdown ## Subtitle Style
font_size    = 24       # @param {type:"slider", min:12, max:72, step:2}
font_color   = "white"  # @param ["white", "yellow", "cyan", "black", "green"]
outline_size = 1        # @param {type:"slider", min:0, max:5, step:1}
shadow_size  = 1        # @param {type:"slider", min:0, max:3, step:1}
position     = "bottom" # @param ["bottom", "top"]
margin_v     = 45       # @param {type:"slider", min:0, max:150, step:5}
margin_lr    = 20       # @param {type:"slider", min:0, max:200, step:10}

# @markdown ## Google Drive Export
export_to_google_drive = False  # @param {type:"boolean"}
# @markdown Copy each finished MP4 to your Google Drive `My Drive` folder.
# @markdown Requires the **Setup cell** to be run first with **Mount Google Drive** checked.

# ASS color format: &HAABBGGRR& — AA=00 means fully opaque
_COLOR_MAP = {
    "white":  "&H00FFFFFF&",
    "yellow": "&H0000FFFF&",
    "cyan":   "&H00FFFF00&",
    "black":  "&H00000000&",
    "green":  "&H0000FF00&",
}
_primary_colour = _COLOR_MAP[font_color]
_outline_colour = "&H00000000&"
_alignment      = 2 if position == "bottom" else 8

if output_resolution == "Original":
    _out_w, _out_h = img_width, img_height
else:
    _out_w, _out_h = map(int, output_resolution.split("x"))

_out_w = _out_w if _out_w % 2 == 0 else _out_w - 1
_out_h = _out_h if _out_h % 2 == 0 else _out_h - 1

if output_resolution == "Original":
    _scale_filter = "scale=trunc(iw/2)*2:trunc(ih/2)*2"
else:
    _scale_filter = (
        f"scale={_out_w}:{_out_h}:force_original_aspect_ratio=decrease,"
        f"scale=trunc(iw/2)*2:trunc(ih/2)*2,"
        f"pad={_out_w}:{_out_h}:(ow-iw)/2:(oh-ih)/2:black"
    )

# Resolve export destination from the Setup cell (graceful fallback if not run)
_drive_export_dir = globals().get('DRIVE_EXPORT_DIR', None)
if export_to_google_drive:
    if _drive_export_dir and os.path.isdir(_drive_export_dir):
        print(f"Drive export enabled  : {_drive_export_dir}/")
    else:
        print("[WARN] Drive export requested but Google Drive is not mounted.")
        print("       Run the Setup cell with 'Mount Google Drive' checked, then re-run this cell.")

# ── Output path helpers ───────────────────────────────────────────────────────

def _safe_stem(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    safe = "".join(
        c if c.isascii() and (c.isalnum() or c in "-_. ") else "_"
        for c in stem
    ).strip("_")
    return safe[:80] or "output"


_used_output_paths = set()


def _unique_output_path(srt_path):
    """Return a /content/<stem>.mp4 path that hasn't been used yet."""
    stem = _safe_stem(srt_path)
    base = f"/content/{stem}.mp4"
    if base not in _used_output_paths and not os.path.exists(base):
        return base
    i = 2
    while True:
        candidate = f"/content/{stem}_{i}.mp4"
        if candidate not in _used_output_paths and not os.path.exists(candidate):
            return candidate
        i += 1


# ── ffmpeg command builder + runner ──────────────────────────────────────────

def _build_cmd(encoder, audio_path, output_path, video_duration, font_name):
    """Return the complete ffmpeg command list for one encode."""
    _fs = (
        f"PlayResX={_out_w},"
        f"PlayResY={_out_h},"
        f"FontName={font_name},"
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
    _subtitle_filter = (
        f"subtitles='{TMP_SRT}'"
        f":charenc=UTF-8"
        f":force_style='{_fs}'"
    )
    _vf = f"{_scale_filter},format=yuv420p,{_subtitle_filter}"

    if encoder == 'h264_nvenc':
        _rc_args = [str(video_crf) if a is None else a for a in _hw['nvenc_rc_args']]
        _enc_args = ["-c:v", "h264_nvenc", *_rc_args, "-preset", video_quality]
    else:
        _enc_args = ["-c:v", "libx264", "-crf", str(video_crf), "-preset", video_quality]

    return [
        "ffmpeg", "-y",
        "-framerate", "1", "-loop", "1", "-i", TMP_COVER,
        "-i", audio_path,
        "-vf", _vf,
        "-af", "asetpts=PTS-STARTPTS,apad",
        "-r", "25",
        *_enc_args,
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        "-pix_fmt", "yuv420p",
        "-t", str(video_duration),
        "-movflags", "+faststart",
        output_path,
    ]


def _run_ffmpeg(cmd):
    """Run ffmpeg with CUDA-aware environment, stream progress, return (returncode, last_lines)."""
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        env=_CUDA_ENV,
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


# ── Phase 11–12: Batch Encode Loop ───────────────────────────────────────────

_results = []   # list of (output_path, success, error_msg, drive_dest)

for _pair_idx, (_audio_path, _srt_path) in enumerate(pairs, 1):
    _pair_label = f"[{_pair_idx}/{len(pairs)}]"
    print(f"\n{'='*60}")
    print(f"{_pair_label} Audio : {os.path.basename(_audio_path)}")
    print(f"{_pair_label} SRT   : {os.path.basename(_srt_path)}")
    print("="*60)

    try:
        # ── 11a: Audio validation + duration probe ────────────────────────────
        _audio_probe = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1",
             _audio_path],
            capture_output=True, text=True,
        )
        if _audio_probe.returncode != 0:
            raise RuntimeError(
                f"Audio file corrupt or unsupported:\n{_audio_probe.stderr.strip()}"
            )
        try:
            _audio_dur = float(_audio_probe.stdout.strip())
            print(f"Audio duration : {_audio_dur:.3f}s")
        except ValueError:
            _audio_dur = None
            print("[WARN] Could not read audio duration — will use SRT duration.")

        # ── 11b: SRT validation + preprocessing ──────────────────────────────
        if os.path.getsize(_srt_path) == 0:
            raise RuntimeError("SRT file is empty.")

        _srt_dur = _preprocess_srt(_srt_path)
        _srt_mm  = int(_srt_dur // 60)
        _srt_ss  = int(_srt_dur % 60)
        print(f"SRT duration   : {_srt_dur:.3f}s  ({_srt_mm:02d}:{_srt_ss:02d})")
        print(f"SRT sanitized  → {TMP_SRT}")

        # ── 11c: Duration resolution ──────────────────────────────────────────
        _video_dur = _srt_dur
        if _audio_dur is not None:
            if _audio_dur > _srt_dur:
                _video_dur = _audio_dur
                print(
                    f"[INFO] Audio ({_audio_dur:.1f}s) longer than SRT "
                    f"({_srt_dur:.1f}s) — extending video to audio length."
                )
            elif _audio_dur < _srt_dur - 1.0:
                print(
                    f"[INFO] Audio ({_audio_dur:.1f}s) shorter than SRT "
                    f"({_srt_dur:.1f}s) — silence will pad the end."
                )

        # ── 11d: Output path (collision-safe) ─────────────────────────────────
        _out_path = _unique_output_path(_srt_path)
        _used_output_paths.add(_out_path)
        print(f"Output path    : {_out_path}")

        # ── 11e: Font selection (CJK auto-detect per SRT) ─────────────────────
        with open(TMP_SRT, encoding="utf-8") as _f:
            _srt_text = _f.read()
        _font_name = FONT_CJK if _has_cjk(_srt_text) else FONT_LATIN

        _mm = int(_video_dur // 60)
        _ss = int(_video_dur % 60)
        _enc_label = "NVENC CQ" if _hw['encoder'] == 'h264_nvenc' else "x264 CRF"
        print(
            f"\nRendering {_mm:02d}:{_ss:02d} at {_out_w}x{_out_h} | "
            f"{_enc_label} {video_crf} | preset={video_quality} | "
            f"encoder={_hw['encoder']} | font={_font_name}\n"
        )

        # ── 11f: ffmpeg encode ────────────────────────────────────────────────
        _active_encoder = _hw['encoder']
        _rc, _last_lines = _run_ffmpeg(
            _build_cmd(_active_encoder, _audio_path, _out_path, _video_dur, _font_name)
        )

        _nvenc_fail_markers = (
            "nvenc", "No capable devices", "Cannot load", "CUDA_ERROR",
            "nvcuvid", "Encoder not found",
        )
        if _rc != 0 and _active_encoder == 'h264_nvenc':
            _tail_lower = "\n".join(_last_lines).lower()
            if any(m.lower() in _tail_lower for m in _nvenc_fail_markers):
                print("[WARN] NVENC encoder failed — seamlessly retrying with CPU libx264...")
                _active_encoder = 'libx264'
                _rc, _last_lines = _run_ffmpeg(
                    _build_cmd('libx264', _audio_path, _out_path, _video_dur, _font_name)
                )

        if _rc != 0:
            _tail = "\n".join(_last_lines)
            _hint = ""
            if "Invalid option" in _tail or "Unknown encoder" in _tail:
                _hint = "Hint: encoder unavailable — run:  !apt install -y ffmpeg"
            elif "No such file" in _tail:
                _hint = "Hint: input file not found — check /content/input/ contents."
            elif "subtitles" in _tail.lower() or "ass" in _tail.lower():
                _hint = ("Hint: subtitle filter error — inspect /tmp/sanitized_subtitles.srt\n"
                         "      Likely cause: libass not compiled into this ffmpeg build.")
            elif "Invalid data" in _tail or "moov atom" in _tail:
                _hint = "Hint: audio file may be corrupt or in an unsupported format."
            elif "not divisible" in _tail:
                _hint = "Hint: dimension parity error — please report this bug."
            raise RuntimeError(
                f"ffmpeg exited with code {_rc}\nLast output:\n{_tail}"
                + (f"\n{_hint}" if _hint else "")
            )

        # ── 12: Output verification ───────────────────────────────────────────
        if not os.path.exists(_out_path) or os.path.getsize(_out_path) == 0:
            raise RuntimeError("Output file was not created or is empty.")

        _size_mb = os.path.getsize(_out_path) / (1024 * 1024)
        _verify = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "stream=codec_type,codec_name,width,height,duration",
             "-of", "default=noprint_wrappers=1",
             _out_path],
            capture_output=True, text=True,
        )
        print(f"\n✓  {_out_path}  ({_size_mb:.2f} MB)")
        if _verify.returncode != 0 or not _verify.stdout.strip():
            print("[WARN] ffprobe could not verify output streams — file may be corrupt.")
        else:
            print(_verify.stdout.strip())

        # ── 13: Google Drive export ───────────────────────────────────────────
        _drive_dest = None
        if export_to_google_drive:
            if _drive_export_dir and os.path.isdir(_drive_export_dir):
                _drive_dest = os.path.join(_drive_export_dir, os.path.basename(_out_path))
                shutil.copy2(_out_path, _drive_dest)
                print(f"Exported to Drive  : {_drive_dest}")
            else:
                print("[WARN] Drive export skipped — Google Drive not mounted.")
                print("       Run the Setup cell with 'Mount Google Drive' checked.")

        _results.append((_out_path, True, "", _drive_dest))

    except (Exception, SystemExit) as _pair_err:
        _err_msg = str(_pair_err).strip()
        _results.append(("", False, _err_msg, None))
        print(f"\n[ERROR] Pair {_pair_idx}/{len(pairs)} failed — skipping.\n{_err_msg}\n")

# ── Final Batch Summary ───────────────────────────────────────────────────────

print(f"\n{'='*60}")
_n_ok   = sum(ok for _, ok, _, _ in _results)
_n_fail = len(_results) - _n_ok
print(
    f"Batch complete : {_n_ok}/{len(_results)} succeeded"
    + (f"  ({_n_fail} failed)" if _n_fail else "")
)
print()
for _path, _ok, _err, _ddest in _results:
    if _ok:
        _sz = os.path.getsize(_path) / (1024 * 1024)
        _note = f"  → Drive: {_ddest}" if _ddest else ""
        print(f"  OK    {_path}  ({_sz:.2f} MB){_note}")
    else:
        print(f"  FAIL  {_err[:120]}")
print()
if _n_ok:
    _any_drive = any(d for _, _, _, d in _results)
    if _any_drive:
        print(f"Files exported to Google Drive : {_drive_export_dir}/")
    if not export_to_google_drive or not _any_drive:
        print("Download: right-click each file in the Files panel (📁 left sidebar) → Download")
        print("⚠️  Download before closing the session — /content/ is erased on disconnect.")