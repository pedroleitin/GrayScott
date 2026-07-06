# Gray-Scott Studio

An interactive **Gray-Scott reaction–diffusion** playground that runs entirely in the
browser, with a designer-grade UI and clean **SVG / PNG** export.

It's a single, dependency-free HTML file — open it and go.

## Features

- **Real-time simulation** on a Canvas 2D grid (resolution up to 1024²).
- **Pattern presets** — Mitosis, Coral, Spots, Waves, Mazes, Cells — plus live
  Feed / Kill / Speed / Resolution / Blur / Contrast controls.
- **Brush** — paint on the canvas in three modes:
  - `Seed` — inject reaction (temporary perturbation),
  - `Wall` — draw a **persistent obstacle trail** the pattern flows around,
  - `Erase` — remove wall trails.
- **Text collider** — type text that carves into the pattern, with font selection,
  size, draggable placement, black/white color and an optional contrasting border.
- **Image halftone** — drop an image and let its luminance modulate line thickness
  (dark → thick, light → thin), with Brightness / Contrast / Thinnest / Thickest.
- **Fill** — seed the whole canvas in one click.
- **Export**
  - **SVG** — vectorized via marching squares → Catmull-Rom béziers, with clean
    borders and selectable trace detail (2× / 3× / 4×). Deterministic (independent
    of window size).
  - **PNG** — high-res (1024px) reproducing the on-screen blur+contrast look.
  - **PNG sequence** — 120 frames packed into a `.zip`.
- **Light / dark theme** toggle.

## Usage

Just open `gray_scott_smooth_svg.html` in a modern browser (double-click works, since
it uses `file://`-safe APIs). Optionally serve it:

```bash
python3 -m http.server 8000   # then open http://localhost:8000/gray_scott_smooth_svg.html
```

- **Paint**: click-drag on the canvas (mode set in the *Brush* section).
- **Move text**: drag the dashed text box on the canvas.
- **Generate a full field**: click *Fill*.

## Tech

- **Vanilla HTML + CSS + JavaScript**, single file, no build step, no dependencies
  (fonts via Google Fonts CDN).
- **Canvas 2D** for rendering; the reaction–diffusion is hand-written in JS
  (`Float32Array`, optimized stencil loop).
- **CSS filters** (`blur` + `contrast`) for the smooth organic look.
- Export built on a hand-rolled **marching squares + Catmull-Rom** tracer.
- UI design language inspired by *GRID-GEN-2* (warm paper palette, `#FFC800`
  accent, Outfit + Ubuntu Mono), implemented in plain CSS.

## Project structure

```
gray_scott_smooth_svg.html   # the app (everything is here)
README.md · CHANGELOG.md · BACKLOG.md
CLAUDE.md · copilot.md        # instructions for AI coding assistants
archive/                      # deprecated offline companion (Python + macOS apps)
```

## Roadmap

Next up is a **GPU port** — both a WebGL2 and a WebGPU version — to move the
simulation off the CPU and unlock high resolution at 60fps. See
[`BACKLOG.md`](BACKLOG.md).

## Archive

`archive/` contains an earlier **offline companion** (`gray_scott.py` with
NumPy/numba/scikit-image, a Tkinter GUI, and two macOS AppleScript apps) that
re-ran the simulation and traced SVGs outside the browser. It's no longer part of
the workflow but kept for reference.
