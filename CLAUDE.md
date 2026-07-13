# CLAUDE.md — Gray-Scott Studio

Guidance for AI coding assistants working in this repo.

## What this is

A **single-file, dependency-free** Gray-Scott reaction–diffusion web app:
`index.html`. Vanilla HTML/CSS/JS, no build, no framework. The simulation
runs on the GPU (**WebGL2**, fragment-shader compute over ping-pong float textures);
the CPU only reads back for export. The whole app is one `<style>` block + one large
`<script>` + a tiny theme-toggle `<script>`.

Earlier engines live in `archive/` and are **not** the app: `gray_scott_smooth_svg.html`
(original CPU / Canvas 2D) and `gray_scott_webgpu.html` (WebGPU / WGSL). Don't wire the
app back to them.

## Golden rules

- **Never add a build step or dependencies.** It stays a single file. Fonts via Google
  Fonts CDN are the only external resource. (Note: WebGL2 float textures usually require
  serving over `http(s)://`, not `file://` — that's a browser limitation, not a build.)
- **Preserve every element `id`.** The script binds behavior by `id`; renaming or
  dropping one silently breaks a control. In particular:
  - Slider pairs are wired via `bindSlider('sl-x','vx', …)` — e.g. `sl-f`/`vf`,
    `sl-fs`/`vfs`, `sl-res`/`vres`, `sl-ramp`/`vramp`, `sl-brush`/`vbrush`, etc.
  - `canvas-col`, `canvas-wrap`, `sim`, `brush-cursor`, `fps` are used by the render
    loop / canvas fitting / brush preview.
  - Segmented buttons toggle the `.active` class (patterns dir, brush modes, ramp dir,
    trace detail) — keep that class mechanism.
  - Pill toggles / checkboxes: `col-invert` (Invert inside text), Border checkbox.
  - Patterns use `querySelectorAll('.chip')` with `data-f` / `data-k`.
- **If you remove a control, remove its JS handler too** — a dangling
  `getElementById(...).addEventListener` on a missing element throws and kills the
  whole script.

## Simulation model (WebGL2 — keep in sync if you touch it)

- State: `A`/`B` packed in **2× RGBA32F ping-pong textures** (`stateTex`/`stateFbo`,
  index `src`); walls in an R32F `wallTex`, image luminance in `imgTex`. CPU-side
  mirrors: `A`/`B`/`wall`/`userWall` `Float32Array`/`Uint8Array`.
- Update in a fragment shader (`_FS_UPDATE`): 5-point Laplacian via `texelFetch` with
  toroidal wrap; coefs `0.2` (A) / `0.1` (B), `THRESH=0.18`. Wall cells are forced to
  `A=1, B=0`. **Detail ramp**: a spatial factor `s = 1 - u_ramp*t` (t = horiz/vert/radial
  position) multiplies the Laplacian — smaller `s` = finer features. `s ≤ 1` keeps
  diffusion under the CFL limit, so it stays stable.
- Paint: `Seed` = GPU `splat` shader; `Wall`/`Erase` = CPU `wall` edit + `uploadWall`.
- **Smooth look is all on the GPU** (Safari applies neither `filter: url(#svg)` nor
  `ctx.filter`, so no CSS/SVG filters). `render()` runs at the **display resolution**
  `RW = clientWidth·dpr` (not `N`) into `fxTex`/`fxFbo` RGBA16F ping-pong: `_FS_DISPLAY`
  upsamples the `N` field (bilinear, or nearest when the **Pixelate** toggle is on) and
  thresholds → binary; `_FS_BLUR` = separable Gaussian (radius from `blurPx·RW/clientWidth`,
  capped 48 taps); `_FS_COMPOSE` applies contrast (pivot 0.5) + the fg/bg gradient map and
  draws to the canvas. Colors/blur/contrast are just uniforms — changing them re-renders,
  never touches `A`/`B`/`step`. `resizeCanvas()` sizes the canvas + `fxTex` to `RW`.
- **Resolution change resamples** the current field (readback + bilinear) instead of
  clearing. `Fill` seeds a grid of disks; `Clear` wipes text + brush walls only.

## Export pipeline

`readbackB()` (`gl.readPixels` from the float FBO) → `buildDarkField()` (binary 0/1,
bakes in text/walls/halftone) → `boxBlur` → `upsampleN(…, F)` where `F = traceDetail`
(2/3/4) → `traceLoops` (marching squares, level 0.5, border zeroed so edge features
close) → `resampleLoop` → `catmullRomToBezier` → `<path fill-rule="evenodd">` with
`fill="${fgColor}"` on `fill="${bgColor}"`. The export blur uses a **fixed reference**
`BLUR_REF=512` so the same pattern always exports identically regardless of window size.
PNG export (`renderPNGCanvas`) just `render()`s and scales the finished canvas (color +
blur + contrast are already baked in on the GPU) to the target size.

## Design system (GRID-GEN-2 style, plain CSS)

CSS variables on `:root`, dark mode via `[data-theme="dark"]`:
`--c-bg #f7f5ef`, `--c-panel #f1eee7`, `--c-text #414141`, `--c-border-light`,
`--c-border-medium`, `--c-btn-bg #fff`, `--c-muted`, **`--c-accent #FFC800`**.
Fonts: **Outfit** (UI) + **Ubuntu Mono** (numeric values). Left floating menu
(`#menu`, 340px), dotted `#stage` canvas backdrop, pill buttons that turn yellow on
hover, yellow selection. Menu sections are a **multi-open accordion**; order: Patterns ·
Parameters · Detail ramp · Colors · Brush · Text collider · Image halftone · Export
(Detail ramp / Text collider / Image halftone start collapsed). **Reset/Pause are
floating buttons over the canvas**, not a menu section. Sliders are the SVG_DRAW
filled-pill widget and selects the SVG_DRAW combobox (native `input`/`select` kept hidden
as state). Pattern chips are bold uppercase initials (16px). Colors + checkboxes follow the GRID-GEN-2 hex-field +
circular-swatch / pill-toggle style. Keep new UI consistent — **do not reintroduce
Material Design.**

## Working / verifying changes

- **Serve** the file (`python3 -m http.server`) and open in a browser — WebGL2 float
  textures generally won't run from `file://`. Prefer a headless check for UI changes;
  clean up temp servers/screenshots after. Note: rAF is throttled in an unfocused/headless
  tab, so develop patterns with synchronous `step(n)` loops in tests.
- After editing markup, sanity-check that no `id` was lost and the sim still runs
  (Fill → step → pattern on canvas, no console/GL errors).

## Roadmap & archive

- See `BACKLOG.md` for open items (halftone refinement, export options, two-image blend).
- `archive/` holds earlier engines (CPU, WebGPU) and the deprecated offline
  Python/AppleScript companion. Kept for reference; not part of the current app.
