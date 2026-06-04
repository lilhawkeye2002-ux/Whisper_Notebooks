# Subtitle Feature Implementation TODO List

This document tracks planned subtitle enhancements for the Cover Video Subtitle Burner notebook.

---

## Animation & Effects

- [ ] **Fade In/Fade Out Transitions** - `{\fad()}` smooth appearance/disappearance
- [ ] **Shadow Distance Animation** - `{\shad}` dynamic depth effects
- [ ] **Blur-to-Focus Effect** - `{\blur}` + `{\t()}` cinematic sharpening
- [ ] **Character-by-Character Reveal** - Typewriter effect with `{\kf}`
- [ ] **Color Temperature Shift** - Subtle warm/cool color transitions
- [ ] **Opacity Pulse on Keywords** - `{\alpha}` emphasis breathing effect
- [ ] **Letter Spacing Animation** - `{\fsp}` expanding character spacing
- [ ] **Split-Line Cascade Entry** - Staggered multi-line appearance
- [ ] **Horizontal Slide-In** - Edge-to-center directional motion

---

## Typography & Styling

- [ ] **Background Box/Banner** - Semi-transparent rectangles behind text
- [ ] **Gradient Text Colors** - Two-color gradient fills using SecondaryColour
- [ ] **Multi-Weight Font Support** - Bold/Light variants with Bold parameter
- [ ] **Italic Angle Customization** - Custom slant angles for emphasis
- [ ] **Drop Shadow Custom Offset** - ShadowX/ShadowY directional control
- [ ] **Font Weight & Stroke Customization** - Bold options + custom outline colors
- [ ] **Subtitle Background Box with Opacity** - Guaranteed readability overlay

---

## Content Processing & Text Manipulation

- [ ] **Smart Line Length Balancing** - Pyramid-shaped text distribution
- [ ] **Reading Speed Analysis** - CPS calculation to determine if multiple sentences should be broken up over multiple subtitle lines
- [ ] **Automatic Overlap Detection** - Timing conflict resolution
- [ ] **Punctuation Normalization** - Auto remove em-dashes
- [ ] **Repetition & Stutter Reduction** - Duplicate word collapsing
- [ ] **Sound Effect Enhancement** - Detect and style sound effects/music notation
- [ ] **Automatic Line Breaking** - Linguistic-aware line splitting
- [ ] **Character-Per-Second Validation** - Reading speed analysis and auto-adjustment
- [ ] **Silence Gap Detection** - ffmpeg silencedetect-based timing optimization

---

## Advanced AI Features

- [ ] **Scene Change Detection** - Detect scene boundaries for optimal subtitle timing
- [ ] **Dynamic Font Auto-Scaling** - ML-based text density analysis
- [ ] **Emotion-Driven Styling** - Sentiment analysis color adjustments

---

## Implementation Notes

**Total Features:** 28

**Priority Levels:**
- **High Priority (Foundational):** Fade transitions, Overlap Detection, Line Breaking, Reading Speed Analysis
- **Medium Priority (Quality):** Background Box, Shadow Animation, Smart Balancing, Punctuation Normalization
- **Low Priority (Advanced):** AI features, complex animations

**Implementation Approach:**
- Extend `_preprocess_srt()` function for text processing features
- Modify ASS force_style parameters for typography enhancements
- Add ASS override tags (`{\tag}`) for per-line/per-word effects
- Integrate ML models for AI-powered features (Scene Detection, Emotion Analysis, Auto-Scaling)

**Dependencies:**
- Existing: ffmpeg, libass, PIL, charset-normalizer
- New (as needed): nltk/spaCy (NLP), transformers (AI), librosa (audio analysis)

---

## Completed Features

None yet - implementation starts after planning phase.
