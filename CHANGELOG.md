# Changelog

All notable changes to Gray-Scott Studio. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are `YYYY-MM-DD`.

## [Unreleased]

### Planned
- GPU port of the simulation: **WebGL2** and **WebGPU** versions (hybrid — sim on the
  GPU, read back only for export). See `BACKLOG.md` §4.

## 2026-07-03

### Changed
- **UI redesigned** from Material 3 to the *GRID-GEN-2* design language (plain CSS):
  warm paper palette, `#FFC800` accent, Outfit + Ubuntu Mono fonts, pill buttons with
  yellow hover, dotted canvas backdrop, thin custom sliders/scrollbar.
- **Menu moved to the left** as a fixed floating panel; canvas fills the rest.
- Added a **light / dark theme** toggle.

### Removed
- "Export state → Python" button (and handler) — the offline Python flow is retired.
- Moved the offline companion (`gray_scott.py`, Tkinter GUI, macOS AppleScript apps)
  to `archive/`.

### Added
- `README.md`, `CLAUDE.md`, `copilot.md`, `CHANGELOG.md`.

## 2026-06-25

### Added
- **SVG trace detail** selector (2× / 3× / 4×) for smoother, more detailed vectors.
- *(archived)* Offline Python companion: NumPy + **numba** (parallel JIT) simulation,
  scikit-image SVG trace, native PIL text collider, a Tkinter GUI, and two macOS
  droplet/launcher apps with custom icons.

### Changed
- **SVG export blur decoupled from window size** (fixed `BLUR_REF=512`) so the same
  pattern always exports identically.

## 2026-06-24

### Added
- **Resolution up to 1024** and **Speed up to 50**.
- **Brush: Wall trail** (persistent obstacles, kept in a `userWall` layer that
  survives text edits) and **Erase** mode.
- Menu cards given a distinct background.

### Changed
- Optimized `step()` (interior fast-path) — ~4–5× faster; 1024² became usable.
- `Fill` now uses a fixed seed spacing so it covers the whole canvas at any resolution.

## 2026-06-23

### Added
- **Image halftone** — upload/drag an image whose luminance modulates line thickness,
  with Brightness / Contrast / Thinnest / Thickest controls; drag-and-drop upload.
- **Font selection** for the text collider (Roboto, Montserrat, Oswald, Anton, Bebas
  Neue, Archivo Black, and system fonts).
- **Text border** (contrasting outline) option.
- **Fill** button (seed the whole field); **Export PNG** and **PNG sequence** (ZIP).
- Reorganized controls into *Control* and *Export* sections.

### Changed
- Font size range widened (100–400); resolution raised to 512.
- Layout given more breathing room; canvas respects window height.

### Fixed
- **Broken SVG borders** — outer ring is zeroed before tracing so edge features form
  clean closed loops instead of stray diagonal slivers.
- Page title mojibake (added `<meta charset="utf-8">`).
