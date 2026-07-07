# Changelog

All notable changes to Gray-Scott Studio. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are `YYYY-MM-DD`.

## [Unreleased]

### Planned
- Halftone line refinement / export options. See `BACKLOG.md`.

## 2026-07-06

### Changed
- **`gray_scott_webgl.html` is now the primary app** (WebGL2 GPU engine). The original
  CPU version (`gray_scott_smooth_svg.html`) and the WebGPU port (`gray_scott_webgpu.html`)
  moved to `archive/`, kept for reference. Docs (`README`, `CLAUDE.md`, `copilot.md`)
  updated to match.
- **Resolution changes no longer clear the canvas** — the current field is resampled
  (bilinear readback) instead of wiped. Resolution ceiling raised to **2048²**.

### Added
- **Detail ramp** section — a spatial feature-size gradient (Amount + Horiz / Vert /
  Radial), implemented as a factor `s = 1 - ramp·t` on the Laplacian in the update
  shader (finer features where `s` is smaller; stays stable since `s ≤ 1`).
- **Colors** section — Foreground / Background pickers (hex field + swatch, GRID-GEN-2
  style) that recolor the pattern **instantly without recomputing**, via an SVG
  `feComponentTransfer` **gradient map** layered after blur+contrast (also fixes the
  white fringe the contrast filter produced at edges).
- **Image morph** — drop a second image (B) to blend the halftone luminance A → B with
  a **Blend** slider; the pattern reorganizes live between the two images. Includes:
  **Cross** (linear luminance) and **Dissolve** (spatial reveal) styles; a **Play**
  button with eased (smoothstep) sweep, a **Speed** control and a **Loop** toggle;
  **Swap A↔B** and **Remove B**; and **Export morph** (PNG sequence sweeping the blend).
- **Brush size** slider + a **cursor ring preview** showing the radius to be applied.
- **Clear** button (next to Fill) — removes text + brush walls but keeps the pattern
  and every other setting.
- **Invert** checkbox in the text collider (swaps the colors inside the text);
  **Border** became a checkbox; **image thumbnail preview** in the drop zone.
- **FPS / steps status badge**.
- Pattern chips redesigned as bold uppercase initials (Waves / Mazes last).

## 2026-07-03

### Added (archived engines)
- **WebGL2 GPU engine** (`gray_scott_webgl.html`): A/B in RGBA32F ping-pong textures,
  update fragment shader with `texelFetch` + toroidal wrap; 60 fps up to 2048².
- **WebGPU engine** (`gray_scott_webgpu.html`): WGSL compute shaders, storage-buffer
  ping-pong, async `mapAsync` readback for export. Kept as a comparison.

## 2026-07-03 (UI)

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
