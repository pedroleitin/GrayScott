#!/usr/bin/env python3
"""Gray-Scott reaction-diffusion — render offline em alta resolução + trace SVG limpo.

Companion do gray_scott_smooth_svg.html. Roda a mesma simulação (modelo idêntico)
em NumPy (rápido, sem travar aba) e exporta:
  - PNG em alta resolução (blur + contraste, visual do canvas)
  - SVG vetorizado com scikit-image (find_contours sub-pixel) + Catmull-Rom,
    com detalhe controlável e independente de tamanho de tela.

Deps: numpy, scipy, scikit-image, pillow (todas no miniconda do projeto).

Exemplos:
  python3 gray_scott.py --pattern mitosis --N 384 --steps 5000
  python3 gray_scott.py --F 0.037 --k 0.060 --N 512 --png-size 2048 --svg-size 1024
"""
import argparse, time
import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation
from skimage import measure
from PIL import Image, ImageDraw, ImageFont

try:
    from numba import njit, prange
    HAVE_NUMBA = True
except Exception:
    HAVE_NUMBA = False

# ---- modelo (idêntico ao app JS) ----
DA, DB, DIFF = 1.0, 0.5, 0.2          # JS: nA = a + Da*0.2*lap(A) - a*b^2 + F*(1-a)
THRESH = 0.18                         # preto onde B > THRESH

PATTERNS = {  # mesmos chips do app
    'mitosis': (0.055, 0.062), 'coral': (0.037, 0.060), 'spots': (0.029, 0.057),
    'waves': (0.025, 0.050), 'mazes': (0.014, 0.054), 'cells': (0.039, 0.058),
}


def laplacian(g):
    return (np.roll(g, 1, 0) + np.roll(g, -1, 0)
            + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4.0 * g)


if HAVE_NUMBA:
    @njit(parallel=True, fastmath=True, cache=True)
    def _run_numba(A, B, W, F, k, steps):
        """Double-buffer síncrono (igual ao app), paralelo nas linhas. W!=0 = obstáculo (texto/parede).
        0.2=Da*0.2, 0.1=Db*0.2."""
        N = A.shape[0]
        nA = np.empty_like(A); nB = np.empty_like(B)
        for _ in range(steps):
            for y in prange(N):
                ym = N - 1 if y == 0 else y - 1
                yp = 0 if y == N - 1 else y + 1
                for x in range(N):
                    if W[y, x] != 0:
                        nA[y, x] = 1.0; nB[y, x] = 0.0
                        continue
                    xm = N - 1 if x == 0 else x - 1
                    xp = 0 if x == N - 1 else x + 1
                    a = A[y, x]; b = B[y, x]
                    lapA = A[y, xm] + A[y, xp] + A[ym, x] + A[yp, x] - 4.0 * a
                    lapB = B[y, xm] + B[y, xp] + B[ym, x] + B[yp, x] - 4.0 * b
                    abb = a * b * b
                    na = a + 0.2 * lapA - abb + F * (1.0 - a)
                    nb = b + 0.1 * lapB + abb - (F + k) * b
                    nA[y, x] = 0.0 if na < 0.0 else (1.0 if na > 1.0 else na)
                    nB[y, x] = 0.0 if nb < 0.0 else (1.0 if nb > 1.0 else nb)
            tmp = A; A = nA; nA = tmp
            tmp = B; B = nB; nB = tmp
        return A, B


def simulate(N, F, k, steps, seed='fill', rng=None, obstacle=None):
    rng = rng or np.random.default_rng(0)
    A = np.ones((N, N), np.float32)
    B = np.zeros((N, N), np.float32)
    if seed == 'center':
        r = max(4, N // 24); c = N // 2
        A[c-r:c+r, c-r:c+r] = 0.5 + rng.random((2*r, 2*r), np.float32) * 0.1
        B[c-r:c+r, c-r:c+r] = 0.25 + rng.random((2*r, 2*r), np.float32) * 0.1
    else:  # 'fill' — sementes espalhadas numa grade (cobre a tela toda, como o botão Fill)
        sp = 8
        for gy in range(sp, N, sp):
            for gx in range(sp, N, sp):
                cy = gy + int(rng.integers(-sp//2, sp//2)); cx = gx + int(rng.integers(-sp//2, sp//2))
                y0, y1 = max(0, cy-2), min(N, cy+3); x0, x1 = max(0, cx-2), min(N, cx+3)
                A[y0:y1, x0:x1] = 0.5; B[y0:y1, x0:x1] = 0.25
    W = np.zeros((N, N), np.uint8) if obstacle is None else obstacle.astype(np.uint8)
    if obstacle is not None:
        m = W.astype(bool); A[m] = 1.0; B[m] = 0.0
    if HAVE_NUMBA:
        A, B = _run_numba(A, B, W, np.float32(F), np.float32(k), int(steps))
    else:
        wb = W.astype(bool)
        for _ in range(steps):
            abb = A * B * B
            A += DA * DIFF * laplacian(A) - abb + F * (1.0 - A)
            B += DB * DIFF * laplacian(B) + abb - (F + k) * B
            np.clip(A, 0, 1, out=A); np.clip(B, 0, 1, out=B)
            if obstacle is not None:
                A[wb] = 1.0; B[wb] = 0.0
    return A, B


def load_state(path):
    """Carrega o dark field exportado pelo app (botão 'Export state').
    JSON: {N, F, k, wallColor, field=base64 de N*N bytes 0/1}. É o padrão exato da tela."""
    import base64, json
    d = json.load(open(path))
    N = int(d['N'])
    dark = np.frombuffer(base64.b64decode(d['field']), np.uint8).astype(np.float32).reshape(N, N)
    return dark, N, float(d.get('F', 0.0)), float(d.get('k', 0.0))


def render_png(dark, out_size, blur_sigma=1.2, sharp=8.0):
    """Campo binário (0/1) -> blur -> contraste (emula blur+contrast do canvas), upscale nítido."""
    N = dark.shape[0]
    field = dark.astype(np.float32)
    g = gaussian_filter(field, blur_sigma)
    g = np.asarray(Image.fromarray((g * 255).astype(np.uint8), 'L')
                   .resize((out_size, out_size), Image.BICUBIC), np.float32) / 255.0
    v = np.clip((0.5 - g) * sharp + 0.5, 0, 1)     # preto onde a região é escura
    return Image.fromarray((v * 255).astype(np.uint8), 'L')


def catmull_rom_closed(pts):
    """Loop fechado Catmull-Rom -> cubic bezier (porte do app JS)."""
    n = len(pts)
    if n < 3:
        return "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z"
    d = f"M{pts[0][0]:.2f},{pts[0][1]:.2f}"
    for i in range(n):
        p0 = pts[(i-1) % n]; p1 = pts[i]; p2 = pts[(i+1) % n]; p3 = pts[(i+2) % n]
        c1x = p1[0] + (p2[0]-p0[0])/6; c1y = p1[1] + (p2[1]-p0[1])/6
        c2x = p2[0] - (p3[0]-p1[0])/6; c2y = p2[1] - (p3[1]-p1[1])/6
        d += f"C{c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {p2[0]:.2f},{p2[1]:.2f}"
    return d + "Z"


def trace_svg(dark, out_size, blur_sigma=1.2, simplify=0.75, smooth=True, F=0., k=0.):
    """find_contours sub-pixel num campo borrado, simplifica (Douglas-Peucker) e
    monta paths bezier suaves. Border padding fecha features que tocam a borda."""
    N = dark.shape[0]
    field = gaussian_filter(dark.astype(np.float32), blur_sigma)
    pad = np.zeros((N + 2, N + 2), np.float32); pad[1:-1, 1:-1] = field
    paths = []
    for c in measure.find_contours(pad, 0.5):
        c = measure.approximate_polygon(c, simplify)            # reduz pontos
        if len(c) < 4:
            continue
        if np.allclose(c[0], c[-1]):                            # tira fecho duplicado
            c = c[:-1]
        pts = [(float(x) - 1.0, float(y) - 1.0) for y, x in c]  # (row,col)->(x,y), desfaz pad
        paths.append(catmull_rom_closed(pts) if smooth else
                     "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + "Z")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{out_size}" height="{out_size}" '
            f'viewBox="0 0 {N} {N}"><title>Gray-Scott F={F:.3f} k={k:.3f}</title>'
            f'<rect width="{N}" height="{N}" fill="white"/>'
            f'<path d="{" ".join(paths)}" fill="black" fill-rule="evenodd"/></svg>'), len(paths)


def find_font(path):
    import os
    cands = ([path] if path else []) + [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/System/Library/Fonts/Supplemental/Impact.ttf',
        '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/System/Library/Fonts/HelveticaNeue.ttc',
        '/Library/Fonts/Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def render_text_walls(N, text, font_path, font_size, fx, fy, border):
    """Texto -> máscara de paredes N×N (1=corpo, 2=borda). Igual ao colisor do app."""
    font = ImageFont.truetype(font_path, int(font_size))
    img = Image.new('L', (N, N), 0)
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=font)
    ox = fx * N - (bb[2] - bb[0]) / 2 - bb[0]
    oy = fy * N - (bb[3] - bb[1]) / 2 - bb[1]
    d.text((ox, oy), text, fill=255, font=font)
    body = np.asarray(img) > 60
    wall = np.zeros((N, N), np.uint8)
    if border > 0:
        wall[binary_dilation(body, iterations=int(border))] = 2
    wall[body] = 1
    return wall


def build_dark(B, twall, wall_color):
    """Combina padrão + texto no dark field final (1=tinta), respeitando wall-color (igual ao app)."""
    dark = (B > THRESH).astype(np.float32)
    if twall is not None:
        body = twall == 1; border = twall == 2
        if wall_color == 'black':
            dark[border] = 0.0; dark[body] = 1.0
        else:
            dark[border] = 1.0; dark[body] = 0.0
    return dark


def main():
    ap = argparse.ArgumentParser(description="Gray-Scott offline render + SVG trace")
    ap.add_argument('--from-state', help="JSON do app (botão 'Export state'): traça o padrão EXATO da tela")
    ap.add_argument('--pattern', choices=PATTERNS, help="preset (define F/k)")
    ap.add_argument('--F', type=float, default=0.055)
    ap.add_argument('--k', type=float, default=0.062)
    ap.add_argument('--N', type=int, default=384, help="resolução da simulação")
    ap.add_argument('--steps', type=int, default=5000)
    ap.add_argument('--seed', choices=['fill', 'center'], default='fill')
    ap.add_argument('--text', default='', help="texto colisor (vazio = nenhum)")
    ap.add_argument('--font', help="caminho de fonte .ttf/.otf (auto-detecta se omitido)")
    ap.add_argument('--font-size', type=int, default=0, help="tamanho em cells (default N/5)")
    ap.add_argument('--text-x', type=float, default=0.5, help="posição X (0-1)")
    ap.add_argument('--text-y', type=float, default=0.5, help="posição Y (0-1)")
    ap.add_argument('--text-border', type=int, default=0, help="borda em cells (0 = sem)")
    ap.add_argument('--wall-color', choices=['black', 'white'], default='black')
    ap.add_argument('--rng', type=int, default=0)
    ap.add_argument('--png-size', type=int, default=2048)
    ap.add_argument('--svg-size', type=int, default=1024)
    ap.add_argument('--blur', type=float, default=1.2, help="sigma do blur (cells)")
    ap.add_argument('--simplify', type=float, default=0.75, help="tolerância DP (cells); menor = mais detalhe")
    ap.add_argument('--no-smooth', action='store_true')
    ap.add_argument('--out', default='gray_scott_py')
    a = ap.parse_args()
    if a.pattern:
        a.F, a.k = PATTERNS[a.pattern]

    t0 = time.time()
    twall = None
    if a.from_state:
        dark, a.N, a.F, a.k = load_state(a.from_state)
        a.seed = 'state'
    else:
        if a.text:
            fp = find_font(a.font)
            if not fp:
                ap.error("nenhuma fonte encontrada; passe --font /caminho/fonte.ttf")
            twall = render_text_walls(a.N, a.text, fp, a.font_size or a.N // 5,
                                      a.text_x, a.text_y, a.text_border)
        obstacle = (twall != 0) if twall is not None else None
        _, B = simulate(a.N, a.F, a.k, a.steps, a.seed, np.random.default_rng(a.rng), obstacle)
        dark = build_dark(B, twall, a.wall_color)
    t_sim = time.time() - t0

    t0 = time.time()
    render_png(dark, a.png_size, a.blur).save(f"{a.out}.png")
    svg, nloops = trace_svg(dark, a.svg_size, a.blur, a.simplify, not a.no_smooth, a.F, a.k)
    open(f"{a.out}.svg", 'w').write(svg)
    t_out = time.time() - t0

    import os
    print(f"F={a.F:.3f} k={a.k:.3f} N={a.N} steps={a.steps} seed={a.seed}")
    engine = 'state(load)' if a.from_state else ('numba' if HAVE_NUMBA else 'numpy')
    print(f"engine: {engine}   sim: {t_sim:.2f}s   export: {t_out:.2f}s   loops: {nloops}")
    print(f"PNG {a.png_size}px: {os.path.getsize(a.out+'.png')/1024:.0f} KB -> {a.out}.png")
    print(f"SVG {a.svg_size}px: {os.path.getsize(a.out+'.svg')/1024:.0f} KB -> {a.out}.svg")


if __name__ == '__main__':
    main()
