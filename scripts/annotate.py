#!/usr/bin/env python3
"""Interactive bullet-hole annotation tool.

Click on bullet holes in the displayed image to mark them.
Annotations are saved in the same JSON format used by the ML pipeline.

Controls:
    Left-click      Add a point
    Right-click     Remove the nearest point
    Ctrl+Z          Undo last added point
    S               Save annotation and quit
    Q / Escape      Quit without saving

Usage:
    python scripts/annotate.py data2/IMG_2984.jpg
    python scripts/annotate.py data2/IMG_2984.HEIC --out data2/annotations/IMG_2984.json
"""

import argparse
import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # HEIC support unavailable; JPEG/PNG still work

from PIL import Image, ImageTk


MAX_DISPLAY = 1200  # max display dimension in pixels
RADIUS = 8          # marker circle radius in display pixels
COLOR_NEW = "#ff2020"
COLOR_EXISTING = "#ff8800"


def fit_image(img, max_dim):
    """Return a resized PIL image and the scale factor applied."""
    w, h = img.size
    scale = min(max_dim / w, max_dim / h, 1.0)
    if scale < 1.0:
        new_w, new_h = int(w * scale), int(h * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    return img, scale


class AnnotationTool:
    def __init__(self, root, image_path, out_path, existing_points):
        self.root = root
        self.image_path = image_path
        self.out_path = out_path
        self.scale = 1.0

        self._load_image()

        orig_w, orig_h = self.orig_size
        self.points = [
            (int(x * self.scale), int(y * self.scale))
            for x, y in existing_points
        ]

        root.title(f"Annotate: {os.path.basename(image_path)}")
        root.resizable(False, False)

        self._build_ui()
        self._redraw()

        root.bind("<KeyPress-s>", lambda _: self._save())
        root.bind("<KeyPress-S>", lambda _: self._save())
        root.bind("<KeyPress-q>", lambda _: self._quit())
        root.bind("<KeyPress-Q>", lambda _: self._quit())
        root.bind("<Escape>",     lambda _: self._quit())
        root.bind("<Control-z>",  lambda _: self._undo())

    def _load_image(self):
        img = Image.open(self.image_path).convert("RGB")
        self.orig_size = img.size  # (W, H)
        display_img, self.scale = fit_image(img, MAX_DISPLAY)
        self.display_size = display_img.size
        self.tk_image = ImageTk.PhotoImage(display_img)

    def _build_ui(self):
        disp_w, disp_h = self.display_size

        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=4)

        self.status_var = tk.StringVar()
        tk.Label(top, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Button(top, text="Save (S)", command=self._save).pack(side=tk.RIGHT, padx=2)
        tk.Button(top, text="Undo (Ctrl+Z)", command=self._undo).pack(side=tk.RIGHT, padx=2)

        self.canvas = tk.Canvas(self.root, width=disp_w, height=disp_h, cursor="crosshair")
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<Button-3>", self._on_right_click)

        hint = tk.Label(
            self.root,
            text="Left-click: add point    Right-click: remove nearest    S: save    Q/Esc: quit",
            fg="#555",
        )
        hint.pack(side=tk.BOTTOM, pady=2)

    def _redraw(self):
        canvas = self.canvas
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        for i, (dx, dy) in enumerate(self.points):
            r = RADIUS
            canvas.create_oval(
                dx - r, dy - r, dx + r, dy + r,
                outline=COLOR_NEW, width=2,
            )
            canvas.create_text(dx + r + 2, dy, text=str(i + 1), anchor=tk.W, fill=COLOR_NEW, font=("Arial", 9))

        self.status_var.set(
            f"{os.path.basename(self.image_path)}  |  "
            f"original {self.orig_size[0]}x{self.orig_size[1]}  |  "
            f"points: {len(self.points)}"
        )

    def _on_left_click(self, event):
        self.points.append((event.x, event.y))
        self._redraw()

    def _on_right_click(self, event):
        if not self.points:
            return
        mx, my = event.x, event.y
        idx = min(range(len(self.points)), key=lambda i: (self.points[i][0] - mx) ** 2 + (self.points[i][1] - my) ** 2)
        self.points.pop(idx)
        self._redraw()

    def _undo(self):
        if self.points:
            self.points.pop()
            self._redraw()

    def _to_orig_coords(self):
        s = self.scale
        return [[int(x / s), int(y / s)] for x, y in self.points]

    def _save(self):
        orig_w, orig_h = self.orig_size
        ann = {
            "points": self._to_orig_coords(),
            "n_points": len(self.points),
            "img_width": orig_w,
            "img_height": orig_h,
        }
        os.makedirs(os.path.dirname(os.path.abspath(self.out_path)), exist_ok=True)
        with open(self.out_path, "w") as f:
            json.dump(ann, f, indent=2)
        print(f"Saved {len(self.points)} point(s) to: {self.out_path}")
        self.root.destroy()

    def _quit(self):
        if self.points:
            if not messagebox.askyesno("Quit", "Quit without saving?"):
                return
        self.root.destroy()


def default_out_path(image_path):
    stem = os.path.splitext(os.path.basename(image_path))[0]
    img_dir = os.path.dirname(os.path.abspath(image_path))
    ann_dir = os.path.join(img_dir, "annotations")
    return os.path.join(ann_dir, stem + ".json")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", help="Path to image file (.jpg, .png, .heic, ...)")
    parser.add_argument("--out", help="Output JSON path (default: <image_dir>/annotations/<stem>.json)")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        sys.exit(f"Image not found: {args.image}")

    out_path = args.out or default_out_path(args.image)

    existing_points = []
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing_points = json.load(f).get("points", [])
        print(f"Loaded {len(existing_points)} existing point(s) from: {out_path}")

    root = tk.Tk()
    AnnotationTool(root, args.image, out_path, existing_points)
    root.mainloop()


if __name__ == "__main__":
    main()
