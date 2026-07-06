# Copilot instructions — Gray-Scott Studio

Custom instructions for GitHub Copilot / AI assistants. (Mirror of `CLAUDE.md`.)

## Project

A single-file, dependency-free Gray-Scott reaction–diffusion web app:
`gray_scott_smooth_svg.html` — vanilla HTML/CSS/JS, no build, no framework.
One `<style>` + one big `<script>` + a small theme-toggle `<script>`.

## Hard constraints

- Keep it **one file, no dependencies, no build**. Must open from `file://`.
- **Do not rename or remove element `id`s** — the script binds controls by `id`
  (sliders via `bindSlider('sl-x','vx')`; `.active` toggles on segmented buttons;
  `canvas-col`/`canvas-wrap`/`sim` drive rendering). Removing a control means also
  removing its JS handler, or the script throws on load.
- **Do not reintroduce Material Design.** UI follows the GRID-GEN-2 style: warm paper
  palette, accent `#FFC800`, Outfit + Ubuntu Mono, left menu, pill buttons that go
  yellow on hover. Colors are CSS vars (`--c-*`); dark mode via `[data-theme="dark"]`.

## How the app works (quick map)

- Sim: `A`/`B` `Float32Array`, `step(n)` (optimized interior + wrapped edges),
  `THRESH=0.18`, obstacles in `wall`/`userWall`. Smooth look = CSS `blur+contrast`.
- Interaction: mouse/touch drag paints via `paint()` (Seed / Wall / Erase);
  the text overlay `#drag-text` is draggable; `Fill` seeds the whole grid.
- Export: `buildDarkField()` → boxBlur → `upsampleN` → `traceLoops` (marching
  squares) → Catmull-Rom béziers → SVG; PNG and a 120-frame PNG-sequence ZIP.
  SVG blur is decoupled from window size (`BLUR_REF=512`), so exports are
  deterministic.

## Verifying

Serve statically and open in a browser; confirm the sim runs (Fill → step → pattern),
no console errors, and no lost `id`s. Clean up any temp servers afterwards.

## Notes

- Roadmap: GPU port (WebGL2 + WebGPU) — see `BACKLOG.md`.
- `archive/` = deprecated offline Python/AppleScript companion; not part of the app.
