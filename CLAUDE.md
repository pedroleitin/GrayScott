# CLAUDE.md — Gray-Scott Studio

Guidance for AI coding assistants working in this repo.

## What this is

A **single-file, dependency-free** Gray-Scott reaction–diffusion web app:
`gray_scott_smooth_svg.html`. Vanilla HTML/CSS/JS, no build, no framework. The whole
app is one `<style>` block + one large `<script>` + a tiny theme-toggle `<script>`.

## Golden rules

- **Never add a build step or dependencies.** It must stay a single file you can open
  from `file://`. Fonts via Google Fonts CDN are the only external resource.
- **Preserve every element `id`.** The script binds behavior by `id`; renaming or
  dropping one silently breaks a control. In particular:
  - Slider pairs are wired via `bindSlider('sl-x','vx', …)` — e.g. `sl-f`/`vf`,
    `sl-fs`/`vfs`, `sl-res`/`vres`, `sl-bri`/`vbri`, etc.
  - `canvas-col`, `canvas-wrap`, `sim` are used by `fitCanvas()` and the render loop.
  - Segmented buttons (`col-blk`/`col-wht`, `bd-off`/`bd-on`, `ht-off`/`ht-gs`,
    `brush-seed/wall/erase`) toggle the `.active` class — keep that class mechanism.
  - Patterns use `querySelectorAll('.chip')` with `data-f` / `data-k`.
- **If you remove a control, remove its JS handler too** — a dangling
  `getElementById(...).addEventListener` on a missing element throws and kills the
  whole script.

## Simulation model (keep in sync if you touch it)

- State: `A`, `B` `Float32Array(N*N)` with `nA`, `nB` scratch buffers (ping-pong).
- Constants: `Da=1.0`, `Db=0.5`, diffusion coef `0.2`, `THRESH=0.18` (black where
  `B > thr`).
- `step(n)`: optimized interior loop (no bounds checks) + separate edge pass with
  toroidal wrap. Obstacles: `wall`/`userWall` `Uint8Array` (1 = text/painted wall,
  2 = text border); wall cells are forced to `A=1, B=0` each step.
- `render()` writes `ImageData`; the smooth look comes from a **CSS filter**
  `blur(blurPx) contrast(contrastVal)` on the canvas element.
- `Fill` seeds a grid of small disks (spacing 8) so the pattern covers the whole
  field at any resolution.

## Export pipeline

`buildDarkField()` (binary 0/1 field, bakes in text/walls/halftone) →
`boxBlur` → `upsampleN(…, F)` where `F = traceDetail` (2/3/4) →
`traceLoops` (marching squares, level 0.5, border zeroed so edge features close) →
`resampleLoop` → `catmullRomToBezier` → `<path fill-rule="evenodd">`.
The export blur uses a **fixed reference** `BLUR_REF=512` so the same pattern always
exports identically regardless of window size. PNG export (`renderPNGCanvas`)
intentionally mirrors the on-screen size (`simC.clientWidth`).

## Design system (GRID-GEN-2 style, plain CSS)

CSS variables on `:root`, dark mode via `[data-theme="dark"]`:
`--c-bg #f7f5ef`, `--c-panel #f1eee7`, `--c-text #414141`, `--c-border-light`,
`--c-border-medium`, `--c-btn-bg #fff`, `--c-muted`, **`--c-accent #FFC800`**.
Fonts: **Outfit** (UI) + **Ubuntu Mono** (numeric values). Left floating menu
(`#menu`, 340px), dotted `#stage` canvas backdrop, pill buttons that turn yellow on
hover, yellow selection. Keep new UI consistent with this — **do not reintroduce
Material Design.**

## Working / verifying changes

- Serve the file (`python3 -m http.server`, or any static server) and open in a
  browser. Prefer a headless check for UI changes; clean up temp servers/screenshots
  after.
- After editing markup, sanity-check that no `id` was lost and the sim still runs
  (e.g. seed a Fill, step, confirm the canvas has pattern and console has no errors).

## Roadmap & archive

- Next major work: **GPU port (WebGL2 + WebGPU)** — see `BACKLOG.md` §4. Plan is a
  hybrid: run the sim on the GPU (ping-pong textures), read back only for export.
- `archive/` holds the deprecated offline Python/AppleScript companion. Not part of
  the current app; don't wire the app back to it.
