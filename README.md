# Gray-Scott Studio

An interactive **Gray-Scott reaction–diffusion** playground that runs entirely in the
browser, with a designer-grade UI and clean **SVG / PNG** export.

It's a single, dependency-free HTML file — open it and go. The simulation runs on the
GPU via **WebGL2**, so it stays at 60 fps up to 2048².

## Features

- **Real-time GPU simulation** (WebGL2 fragment-shader compute, ping-pong float
  textures) — resolution up to **2048²** at 60 fps.
- **Pattern presets** — Mitosis, Coral, Spots, Cells, Waves, Mazes — plus live
  Feed / Kill / Speed / Resolution / Blur / Contrast controls.
- **Detail ramp** — a spatial feature-size gradient (Horiz / Vert / Radial): the
  pattern gets finer on one side and coarser on the other, on a uniform grid.
- **Colors** — Foreground / Background pickers that recolor the pattern **instantly,
  without recomputing** the simulation (applied as a gradient map over the canvas, so
  the contrast filter never leaves a white fringe).
- **Brush** — paint on the canvas in three modes, with an adjustable **size** and a
  cursor ring preview:
  - `Seed` — inject reaction (temporary perturbation),
  - `Wall` — draw a **persistent obstacle trail** the pattern flows around,
  - `Erase` — remove wall trails.
- **Fill** — seed the whole canvas in one click. **Clear** — remove text + brush
  walls but keep the pattern and every other setting.
- **Resolution change without clearing** — changing Resolution resamples the current
  pattern (bilinear) instead of wiping the field.
- **Text collider** — type text that carves into the pattern, with font selection,
  size, draggable placement, an optional contrasting border, and an **Invert**
  checkbox that swaps the colors inside the text.
- **Image halftone** — drop an image and let its luminance modulate line thickness
  (dark → thick, light → thin), with Brightness / Contrast / Thinnest / Thickest and
  a thumbnail preview in the drop zone. Drop a **second image** to **morph A → B**:
  Cross or Dissolve style, a Blend slider, an eased Play sweep with Speed + Loop,
  Swap / Remove, and an **Export morph** PNG sequence.
- **Export**
  - **SVG** — vectorized via marching squares → Catmull-Rom béziers, with clean
    borders and selectable trace detail (2× / 3× / 4×). Deterministic (independent
    of window size).
  - **PNG** — high-res reproducing the on-screen blur+contrast+color look.
  - **PNG sequence** — frames packed into a `.zip`.
- **FPS / steps status badge**.
- **Light / dark theme** toggle.

## Usage

The app uses WebGL2 float textures, which most browsers only allow over `http(s)://`
(not `file://`). Serve it:

```bash
python3 -m http.server 8000   # then open http://localhost:8000/gray_scott_webgl.html
```

- **Paint**: click-drag on the canvas (mode set in the *Brush* section).
- **Move text**: drag the dashed text box on the canvas.
- **Generate a full field**: click *Fill*.

## Tech

- **Vanilla HTML + CSS + JavaScript**, single file, no build step, no dependencies
  (fonts via Google Fonts CDN).
- **WebGL2** for the simulation: A/B state in RGBA32F ping-pong textures, updated by a
  fragment shader (`texelFetch`, toroidal wrap); walls/image in R32F textures. The CPU
  only reads back for export.
- **CSS filters** (`blur` + `contrast`) plus an SVG `feComponentTransfer` **gradient
  map** for the smooth, colored organic look.
- Export built on a hand-rolled **marching squares + Catmull-Rom** tracer.
- UI design language inspired by *GRID-GEN-2* (warm paper palette, `#FFC800`
  accent, Outfit + Ubuntu Mono), implemented in plain CSS.

## Project structure

```
gray_scott_webgl.html         # the app (everything is here) — WebGL2 engine
README.md · CHANGELOG.md · BACKLOG.md
CLAUDE.md · copilot.md        # instructions for AI coding assistants
archive/                      # earlier versions, kept for reference:
  gray_scott_smooth_svg.html  #   original CPU (Canvas 2D) engine
  gray_scott_webgpu.html      #   WebGPU (WGSL compute) engine
  gray_scott.py, *.app, …     #   deprecated offline Python/AppleScript companion
```

## Archive

`archive/` keeps earlier incarnations for reference:

- **`gray_scott_smooth_svg.html`** — the original **CPU** engine (Canvas 2D, hand-written
  `Float32Array` stencil loop). Superseded by the WebGL2 version but still `file://`-safe.
- **`gray_scott_webgpu.html`** — a **WebGPU** (WGSL compute shader) port, kept as a
  comparison. Feature-complete but not the primary app; WebGL2 was chosen for reach
  (no perf win for this workload at vsync-capped resolutions).
- An **offline companion** (`gray_scott.py` with NumPy/numba/scikit-image, a Tkinter
  GUI, and two macOS AppleScript apps) that re-ran the simulation outside the browser.
  No longer part of the workflow.
