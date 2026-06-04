# Features That Will Never Be Implemented

This document lists subtitle features that were brainstormed during analysis but have been decided against for implementation.

---

## Typography & Styling Features

### Letter Spacing Control (Static)
**Description:** Basic character spacing control without animation.
**Reason:** Animation version is more valuable and covers this use case.

### Custom Color Palettes with Transparency
**Description:** User-defined RGB colors with alpha transparency control beyond the 5-color map.
**Reason:** Complexity vs. utility - existing color map is sufficient for most use cases.

### Multi-Line Alignment Options
**Description:** Left/center/right text alignment control for multi-line subtitles across all 9 ASS alignment positions.
**Reason:** Bottom-center and top-center alignments cover majority of subtitle needs.

### Outline Blur/Glow Effect (Static)
**Description:** Static gaussian blur on outline layer for soft glow/halo effects.
**Reason:** Blur-to-Focus animation feature provides dynamic version with better visual impact.

### ScaleX/ScaleY Text Stretching
**Description:** Independent horizontal and vertical scaling for stretched/condensed text proportions.
**Reason:** Distorts text readability, limited practical applications.

### Rotation and Vertical Text
**Description:** Text rotation capabilities for vertical text layouts or angled text effects.
**Reason:** Reduces readability, niche use case for Western content.

### Two-Layer Subtitles (Main + Translation)
**Description:** Render two subtitle layers simultaneously - primary language at bottom, translation at top.
**Reason:** Clutters screen, better handled by viewer selecting language track.

### Justified Text Alignment
**Description:** Full-justified text alignment for multi-line subtitles with distributed word spacing.
**Reason:** Poor readability on video, inconsistent spacing looks unprofessional.

### Karaoke-Style Color Fill
**Description:** Word-by-word or character-by-character color change effects synchronized to audio timing.
**Reason:** Overlaps with Character-by-Character Reveal feature, karaoke not primary use case.

### Font Fallback Chain
**Description:** Prioritized font fallback list for mixing scripts instead of binary Latin/CJK choice.
**Reason:** Current binary system works well, added complexity not justified.

---

## Accessibility & Localization Features

### Multi-Script Mixed-Language Detection
**Description:** Extend detection to support Arabic, Hebrew, Thai, Devanagari, Cyrillic with appropriate font fallbacks.
**Reason:** Extremely niche use case, requires extensive font library management.

### Right-to-Left (RTL) Text Support
**Description:** Automatic detection and proper rendering of RTL languages with correct text direction.
**Reason:** Complex bidirectional text algorithm, limited audience for RTL subtitle burning.

### Dyslexia-Friendly Font Mode
**Description:** OpenDyslexic or Lexend font option with weighted bottom-heavy letters.
**Reason:** Niche accessibility need, can be manually configured if needed.

### High Contrast & Color Blindness Modes
**Description:** Preset color schemes optimized for different types of color vision deficiency.
**Reason:** Background box with opacity addresses contrast needs universally.

### Karaoke Word-Level Timing
**Description:** Progressive word highlighting for language learning and accessibility.
**Reason:** Character-by-Character Reveal covers similar ground, word timing complex to implement.

### Multi-Language SRT Merging
**Description:** Dual-language subtitles by vertically offsetting two SRT files.
**Reason:** Clutters screen, better handled by separate video versions or viewer selection.

### Hearing Impaired SDH Support
**Description:** Detect and preserve sound effect descriptions with distinct styling.
**Reason:** Sound Effect Enhancement feature covers this need.

### Vertical Text Rendering
**Description:** Traditional vertical text layout for classical Japanese, Chinese, Mongolian content.
**Reason:** Extremely niche, Western horizontal reading is standard for video.

### Unicode Normalization & Emoji
**Description:** NFC normalization and proper color emoji display using Noto Color Emoji font.
**Reason:** Unicode issues rare in practice, emoji rendering not critical for subtitles.

### Localized Number/Date Formatting
**Description:** Auto-detect and format numbers/dates according to detected language conventions.
**Reason:** Transcription already in correct format, auto-formatting may introduce errors.

### Closed Caption Positioning Zones
**Description:** Multiple simultaneous subtitle tracks positioned at different screen locations.
**Reason:** Overly complex, standard bottom positioning works for vast majority of content.

---

## Animation & Effects Features

### Karaoke Word Highlighting
**Description:** Words change color progressively as spoken, synchronized with audio timing.
**Reason:** Overlaps with other animation features, not core subtitle burning use case.

### Vertical Position Animation
**Description:** Subtitles slide up from bottom or down from top into final position.
**Reason:** Horizontal Slide-In provides directional animation, vertical adds minimal value.

### Scale/Zoom Animation
**Description:** Subtitles start smaller and grow to 100% size over time.
**Reason:** Can be distracting, less professional than fade transitions.

### Rotating Outline/Border
**Description:** Subtitle outline color cycles through predefined sequence or thickness pulses.
**Reason:** Too flashy, distracts from content readability.

### Bouncing Baseline Effect
**Description:** Subtitles briefly bounce on entry with physics-based motion.
**Reason:** Too playful for general use, contradicts professional subtitle standards.

### Alternating Line Positions
**Description:** Multi-line subtitles alternate vertical positions to prevent overlap.
**Reason:** Automatic Overlap Detection handles timing conflicts more elegantly.

---

## Content Processing Features

### Profanity & Content Filtering
**Description:** Context-aware profanity detection and censoring with configurable word lists.
**Reason:** Content filtering should be done at source, subtitle level filtering incomplete solution.

### Speaker Diarization Labels
**Description:** Detect speaker tags in SRT files and apply consistent color coding.
**Reason:** Speaker identification better handled during transcription phase.

### Trailing Ellipsis Continuation
**Description:** Reduce gap between sentence fragments split across consecutive cues.
**Reason:** Overlap Detection and Line Breaking features address timing/splitting issues.

### URL & Email Sanitization
**Description:** Detect and remove/shorten URLs and email addresses in subtitle text.
**Reason:** Content editing should happen before subtitle generation, not during burning.

### Unicode Normalization & Cleanup
**Description:** NFKC normalization, zero-width character removal, control code cleanup.
**Reason:** Rare edge case, modern SRT generation already handles this.

### Language-Specific Formatting
**Description:** Apply language-specific rules like CJK punctuation spacing, quotation mark styles.
**Reason:** Over-engineering, transcription should already have correct formatting.

### Subtitle Position Collision Avoidance
**Description:** Dynamically reposition cues to avoid overlapping with logos or graphics.
**Reason:** Cover image is static, collision avoidance not applicable to current use case.

### Numeric Formatting
**Description:** Add thousand separators, standardize units, format currency symbols.
**Reason:** Numbers should be formatted correctly in source transcription.

---

## Advanced AI Features

### Automatic Speech-to-Subtitle (Whisper)
**Description:** Generate timestamped subtitles directly from audio using Whisper model.
**Reason:** This is a separate transcription tool, outside scope of subtitle burning pipeline.

### Neural Translation
**Description:** Automatically translate existing subtitles using transformer-based MT models.
**Reason:** Translation is a separate service, better handled by dedicated translation tools.

### Intelligent Segmentation
**Description:** Break long lines into readable chunks using semantic sentence boundary detection.
**Reason:** Smart Line Length Balancing and Automatic Line Breaking cover this need.

### GPU Profanity Filter
**Description:** Context-aware toxicity detection using transformer models.
**Reason:** Profanity filtering better handled at content creation stage, not burning stage.

### Speaker Diarization (AI)
**Description:** Detect multiple speakers using pyannote.audio and assign unique colors.
**Reason:** Speaker identification should be done during transcription, not video burning.

### Background Music Detection
**Description:** Use audio classification to detect music and adjust subtitle positioning.
**Reason:** Static cover image use case doesn't benefit from dynamic positioning.

### Automatic Typo Correction
**Description:** Fix transcription errors using GPT-based or T5 grammar correction.
**Reason:** Errors should be fixed in source SRT, not auto-corrected during burning (may introduce new errors).

### NER Glossary Auto-Linking
**Description:** Detect technical terms and names, generate companion glossary.
**Reason:** Glossary generation is separate content enhancement, outside scope of subtitle burning.

### GPU-Accelerated OCR
**Description:** Extract text from image-based subtitle tracks using Tesseract OCR.
**Reason:** OCR is a preprocessing step, separate from subtitle burning workflow.

### Adaptive Bitrate Rendering
**Description:** Generate multiple video versions with subtitles scaled per resolution.
**Reason:** Adds significant complexity, users can encode multiple times if needed.

### Lip-Sync Confidence Scoring
**Description:** Score subtitle timing accuracy using audio-visual alignment.
**Reason:** Static cover image makes lip-sync irrelevant, future video support uncertain.

### Caption Quality Assessment
**Description:** Evaluate subtitle quality using transformer-based coherence models.
**Reason:** Quality assessment is a validation tool, should be separate from burning process.

---

## Summary

**Total Features Rejected:** 47

**Primary Reasons for Rejection:**
1. **Outside Scope:** Features belong in transcription/translation/preprocessing tools (18 features)
2. **Overlapping Functionality:** Already covered by selected features (9 features)
3. **Niche Use Case:** Limited audience or extremely specific scenarios (12 features)
4. **Readability Concerns:** Features that reduce subtitle legibility (5 features)
5. **Complexity vs. Value:** Implementation effort doesn't justify limited benefit (3 features)

The 28 features selected for implementation represent the highest-value enhancements that:
- Directly improve subtitle readability and visual quality
- Are appropriate for the cover image + audio workflow
- Have broad applicability across content types
- Can be implemented within the existing ffmpeg/libass pipeline
- Don't duplicate functionality or add unnecessary complexity
