#!/usr/bin/env python3
"""Mini-GUI para o gray_scott.py — gera PNG + SVG sem terminal.

Reaproveita toda a engine do gray_scott.py (simulação numba, texto colisor,
render PNG, trace SVG). Abre com 'Gray-Scott Studio.app' ou:
    python3 gray_scott_gui.py
"""
import os, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import ImageTk
import gray_scott as gs


class App:
    def __init__(self, root):
        self.root = root
        root.title("Gray-Scott Studio")
        self._preview_ref = None
        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        self.vars = {}

        def row(r, label, key, default, width=10):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="w", pady=2)
            v = tk.StringVar(value=str(default)); self.vars[key] = v
            ttk.Entry(frm, textvariable=v, width=width).grid(row=r, column=1, sticky="w")

        r = 0
        ttk.Label(frm, text="Pattern").grid(row=r, column=0, sticky="w")
        self.pattern = tk.StringVar(value="mitosis")
        cb = ttk.Combobox(frm, textvariable=self.pattern, width=12, state="readonly",
                          values=["custom"] + list(gs.PATTERNS))
        cb.grid(row=r, column=1, sticky="w"); cb.bind("<<ComboboxSelected>>", self.on_pattern); r += 1
        row(r, "Feed (F)", "F", 0.055); r += 1
        row(r, "Kill (k)", "k", 0.062); r += 1
        row(r, "Resolution (N)", "N", 384); r += 1
        row(r, "Steps", "steps", 5000); r += 1
        row(r, "Seed (rng)", "rng", 0); r += 1
        row(r, "Text", "text", "", 18); r += 1
        row(r, "Font size (0=auto)", "font_size", 0); r += 1
        row(r, "Text border", "text_border", 0); r += 1
        ttk.Label(frm, text="Wall color").grid(row=r, column=0, sticky="w")
        self.wall = tk.StringVar(value="black")
        ttk.Combobox(frm, textvariable=self.wall, width=8, state="readonly",
                     values=["black", "white"]).grid(row=r, column=1, sticky="w"); r += 1
        row(r, "Blur", "blur", 1.2); r += 1
        row(r, "Simplify", "simplify", 0.75); r += 1
        row(r, "PNG size", "png_size", 1024); r += 1
        row(r, "SVG size", "svg_size", 1024); r += 1
        ttk.Label(frm, text="Output dir").grid(row=r, column=0, sticky="w")
        self.outdir = tk.StringVar(value=os.path.expanduser("~/Desktop"))
        ttk.Entry(frm, textvariable=self.outdir, width=22).grid(row=r, column=1, sticky="w")
        ttk.Button(frm, text="…", width=3, command=self.browse).grid(row=r, column=2); r += 1
        row(r, "Base name", "out", "gray_scott", 18); r += 1
        self.btn = ttk.Button(frm, text="Generate", command=self.generate)
        self.btn.grid(row=r, column=0, columnspan=2, pady=8, sticky="ew"); r += 1
        self.status = ttk.Label(frm, text="pronto", foreground="#555")
        self.status.grid(row=r, column=0, columnspan=3, sticky="w"); r += 1
        self.preview = ttk.Label(frm, text="(preview)", width=44, anchor="center",
                                 relief="groove")
        self.preview.grid(row=0, column=3, rowspan=r, padx=12, sticky="nsew")

    def on_pattern(self, *_):
        p = self.pattern.get()
        if p in gs.PATTERNS:
            F, k = gs.PATTERNS[p]; self.vars["F"].set(F); self.vars["k"].set(k)

    def browse(self):
        d = filedialog.askdirectory(initialdir=self.outdir.get())
        if d:
            self.outdir.set(d)

    def generate(self):
        try:
            p = {k: v.get() for k, v in self.vars.items()}
            c = dict(N=int(p["N"]), F=float(p["F"]), k=float(p["k"]), steps=int(p["steps"]),
                     rng=int(p["rng"]), text=p["text"].strip(), font_size=int(p["font_size"]),
                     border=int(p["text_border"]), wall=self.wall.get(), blur=float(p["blur"]),
                     simplify=float(p["simplify"]), png=int(p["png_size"]), svg=int(p["svg_size"]),
                     outdir=self.outdir.get(), out=(p["out"].strip() or "gray_scott"))
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {e}"); return
        if not os.path.isdir(c["outdir"]):
            messagebox.showerror("Erro", "Output dir inválido"); return
        self.btn.config(state="disabled"); self.status.config(text="gerando…")
        threading.Thread(target=self._work, args=(c,), daemon=True).start()

    def _work(self, c):
        try:
            twall = None
            if c["text"]:
                fp = gs.find_font(None)
                if not fp:
                    raise RuntimeError("nenhuma fonte encontrada")
                twall = gs.render_text_walls(c["N"], c["text"], fp,
                                             c["font_size"] or c["N"] // 5, 0.5, 0.5, c["border"])
            obstacle = (twall != 0) if twall is not None else None
            _, B = gs.simulate(c["N"], c["F"], c["k"], c["steps"], "fill",
                               np.random.default_rng(c["rng"]), obstacle)
            dark = gs.build_dark(B, twall, c["wall"])
            base = os.path.join(c["outdir"], c["out"])
            im = gs.render_png(dark, c["png"], c["blur"])
            im.save(base + ".png")
            svg, n = gs.trace_svg(dark, c["svg"], c["blur"], c["simplify"], True, c["F"], c["k"])
            with open(base + ".svg", "w") as f:
                f.write(svg)
            thumb = im.copy(); thumb.thumbnail((380, 380))
            self.root.after(0, self._done, thumb, f"OK · {n} loops → {base}.png / .svg")
        except Exception as e:
            self.root.after(0, self._fail, str(e))

    def _done(self, thumb, msg):
        self._preview_ref = ImageTk.PhotoImage(thumb)
        self.preview.config(image=self._preview_ref, text="")
        self.status.config(text=msg, foreground="#1a7f37")
        self.btn.config(state="normal")

    def _fail(self, msg):
        self.status.config(text="erro: " + msg, foreground="#b00")
        self.btn.config(state="normal")
        messagebox.showerror("Erro", msg)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
