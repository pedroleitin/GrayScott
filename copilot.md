# Copilot instructions — Gray-Scott Studio

Custom instructions for GitHub Copilot / AI assistants. (Mirror of `CLAUDE.md`.)

## Project

A single-file, dependency-free Gray-Scott reaction–diffusion web app:
`gray_scott_webgl.html` — vanilla HTML/CSS/JS, no build, no framework. The simulation
runs on the GPU via **WebGL2** (fragment-shader compute over ping-pong float textures);
the CPU only reads back for export. One `<style>` + one big `<script>` + a small
theme-toggle `<script>`.

Earlier engines live in `archive/` and are not the app: `gray_scott_smooth_svg.html`
(original CPU / Canvas 2D) and `gray_scott_webgpu.html` (WebGPU / WGSL).

## Hard constraints

- Keep it **one file, no dependencies, no build**. (WebGL2 float textures usually need
  serving over `http(s)://` rather than `file://` — a browser limitation, not a build.)
- **Do not rename or remove element `id`s** — the script binds controls by `id`
  (sliders via `bindSlider('sl-x','vx')`; `.active` toggles on segmented buttons —
  patterns/brush modes/ramp dir/trace detail; `canvas-col`/`canvas-wrap`/`sim`/
  `brush-cursor`/`fps` drive rendering; checkboxes `col-invert`/Border). Removing a
  control means also removing its JS handler, or the script throws on load.
- **Do not reintroduce Material Design.** UI follows the GRID-GEN-2 style: warm paper
  palette, accent `#FFC800`, Outfit + Ubuntu Mono, left menu, pill buttons that go
  yellow on hover. Colors are CSS vars (`--c-*`); dark mode via `[data-theme="dark"]`.

## How the app works (quick map)

- Sim (GPU): `A`/`B` in 2× RGBA32F ping-pong textures; update fragment shader with a
  5-point Laplacian (`texelFetch`, toroidal wrap), coefs 0.2/0.1, `THRESH=0.18`.
  Walls/image in R32F textures. **Detail ramp** = spatial factor `s=1-u_ramp*t` on the
  Laplacian (finer features where `s` is smaller). Smooth look = CSS `blur+contrast+
  url(#gradmap)`, where `#gradmap` is an SVG gradient map for Foreground/Background
  colors (recolor = update `tableValues`, never recompute the sim).
- Interaction: mouse/touch drag paints via `paint()` (Seed = GPU splat; Wall/Erase =
  CPU `wall` + `uploadWall`), with an adjustable brush size + cursor ring. Text overlay
  `#drag-text` is draggable, with an Invert checkbox. `Fill` seeds the grid; `Clear`
  removes text + brush walls only. Changing Resolution resamples (doesn't clear).
- Export: `readbackB()` → `buildDarkField()` → boxBlur → `upsampleN` → `traceLoops`
  (marching squares) → Catmull-Rom béziers → SVG (fg on bg); PNG and a PNG-sequence ZIP.
  SVG blur is decoupled from window size (`BLUR_REF=512`), so exports are deterministic.

## Verifying

Serve statically (WebGL2 float textures generally won't run from `file://`) and open in
a browser; confirm the sim runs (Fill → step → pattern), no console/GL errors, and no
lost `id`s. rAF is throttled in unfocused/headless tabs — use synchronous `step(n)`
loops in tests. Clean up any temp servers afterwards.

## Notes

- Roadmap / open items — see `BACKLOG.md`.
- `archive/` = earlier engines (CPU `gray_scott_smooth_svg.html`, WebGPU
  `gray_scott_webgpu.html`) + the deprecated offline Python/AppleScript companion. Not
  part of the current app.
