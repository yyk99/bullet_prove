#!/usr/bin/env python3
"""Interactive bullet-hole annotation tool.

Click on bullet holes in the displayed image to mark them.
Annotations are saved in the same JSON format used by the ML pipeline.

Controls:
    Left-click          Add a point
    Right-click         Remove the nearest point
    Scroll wheel        Zoom in / out (centered on cursor)
    Middle-drag         Pan
    Ctrl+Z              Undo last added point
    S                   Save annotation and quit
    Q / Escape          Quit without saving

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


MAX_DISPLAY = 900   # initial canvas dimension (px)
ZOOM_STEP   = 1.25  # zoom factor per scroll tick
ZOOM_MIN    = 0.05
ZOOM_MAX    = 20.0
RADIUS      = 8     # marker circle radius in display pixels
COLOR       = "#ff2020"


class AnnotationTool:
    def __init__(self, root, image_path, out_path, existing_points):
        self.root = root
        self.image_path = image_path
        self.out_path = out_path

        # Original image kept in memory for re-scaling on zoom
        self.orig_img = Image.open(image_path).convert("RGB")
        self.orig_w, self.orig_h = self.orig_img.size

        # Initial zoom: fit the image inside MAX_DISPLAY
        self.zoom = min(MAX_DISPLAY / self.orig_w, MAX_DISPLAY / self.orig_h, 1.0)

        # Points stored in original image space
        self.points = [list(p) for p in existing_points]

        # Pending resize job id (debounce)
        self._resize_job = None
        self.tk_image = None

        root.title(f"Annotate: {os.path.basename(image_path)}")
        self._build_ui()
        self._rebuild_image()
        self._redraw()

        root.bind("<KeyPress-s>", lambda _: self._save())
        root.bind("<KeyPress-S>", lambda _: self._save())
        root.bind("<KeyPress-q>", lambda _: self._quit())
        root.bind("<KeyPress-Q>", lambda _: self._quit())
        root.bind("<Escape>",     lambda _: self._quit())
        root.bind("<Control-z>",  lambda _: self._undo())

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        init_w = min(MAX_DISPLAY, int(self.orig_w * self.zoom))
        init_h = min(MAX_DISPLAY, int(self.orig_h * self.zoom))

        # Top bar
        top = tk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=4)
        self.status_var = tk.StringVar()
        tk.Label(top, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(top, text="Save (S)", command=self._save).pack(side=tk.RIGHT, padx=2)
        tk.Button(top, text="Undo (Ctrl+Z)", command=self._undo).pack(side=tk.RIGHT, padx=2)

        # Canvas + scrollbars
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            frame, width=init_w, height=init_h,
            cursor="crosshair", bg="#333",
        )
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL,   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT,  fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Hint bar
        tk.Label(
            self.root,
            text="Left-click: add    Right-click: remove nearest    Scroll: zoom    Middle-drag: pan    S: save    Q: quit",
            fg="#555",
        ).pack(side=tk.BOTTOM, pady=2)

        # Mouse bindings
        self.canvas.bind("<Button-1>",        self._on_left_click)
        self.canvas.bind("<Button-3>",        self._on_right_click)
        self.canvas.bind("<MouseWheel>",      self._on_scroll)   # Windows / macOS
        self.canvas.bind("<Button-4>",        self._on_scroll)   # Linux scroll up
        self.canvas.bind("<Button-5>",        self._on_scroll)   # Linux scroll down
        self.canvas.bind("<ButtonPress-2>",   self._on_pan_start)
        self.canvas.bind("<B2-Motion>",       self._on_pan_move)

    # ------------------------------------------------------------------
    # Image rendering
    # ------------------------------------------------------------------

    def _rebuild_image(self):
        """Resize orig_img to current zoom and update tk_image + scrollregion."""
        new_w = max(1, int(self.orig_w * self.zoom))
        new_h = max(1, int(self.orig_h * self.zoom))
        resized = self.orig_img.resize((new_w, new_h), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        self.canvas.configure(scrollregion=(0, 0, new_w, new_h))

    def _redraw(self):
        canvas = self.canvas
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        z = self.zoom
        for i, (ox, oy) in enumerate(self.points):
            dx, dy = ox * z, oy * z
            r = RADIUS
            canvas.create_oval(dx - r, dy - r, dx + r, dy + r, outline=COLOR, width=2)
            canvas.create_text(dx + r + 2, dy, text=str(i + 1), anchor=tk.W, fill=COLOR, font=("Arial", 9))

        self.status_var.set(
            f"{os.path.basename(self.image_path)}  |  "
            f"{self.orig_w}x{self.orig_h}  |  "
            f"zoom {self.zoom * 100:.0f}%  |  "
            f"points: {len(self.points)}"
        )

    # ------------------------------------------------------------------
    # Zoom
    # ------------------------------------------------------------------

    def _on_scroll(self, event):
        if event.num == 4 or getattr(event, "delta", 0) > 0:
            factor = ZOOM_STEP
        else:
            factor = 1.0 / ZOOM_STEP

        # Canvas coords under the cursor (accounts for current scroll offset)
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        # Original-image coords under cursor — must stay fixed after zoom
        orig_x = cx / self.zoom
        orig_y = cy / self.zoom

        new_zoom = max(ZOOM_MIN, min(self.zoom * factor, ZOOM_MAX))
        if new_zoom == self.zoom:
            return
        self.zoom = new_zoom

        # Debounce: cancel pending resize and schedule a new one
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(60, self._finish_zoom)

        # Immediately redraw markers at new zoom (image stays stale for 60 ms)
        self._redraw()

        # Shift scroll so the point under the cursor stays fixed
        new_w = int(self.orig_w * self.zoom)
        new_h = int(self.orig_h * self.zoom)
        self.canvas.configure(scrollregion=(0, 0, new_w, new_h))
        self.canvas.xview_moveto((orig_x * self.zoom - event.x) / new_w)
        self.canvas.yview_moveto((orig_y * self.zoom - event.y) / new_h)

    def _finish_zoom(self):
        """Called after scroll stops — rebuild the image at the final zoom."""
        self._resize_job = None
        self._rebuild_image()
        self._redraw()

    # ------------------------------------------------------------------
    # Pan (middle-mouse drag)
    # ------------------------------------------------------------------

    def _on_pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # ------------------------------------------------------------------
    # Point editing
    # ------------------------------------------------------------------

    def _canvas_to_orig(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return int(cx / self.zoom), int(cy / self.zoom)

    def _on_left_click(self, event):
        self.points.append(list(self._canvas_to_orig(event)))
        self._redraw()

    def _on_right_click(self, event):
        if not self.points:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        z = self.zoom
        idx = min(
            range(len(self.points)),
            key=lambda i: (self.points[i][0] * z - cx) ** 2 + (self.points[i][1] * z - cy) ** 2,
        )
        self.points.pop(idx)
        self._redraw()

    def _undo(self):
        if self.points:
            self.points.pop()
            self._redraw()

    # ------------------------------------------------------------------
    # Save / quit
    # ------------------------------------------------------------------

    def _save(self):
        ann = {
            "points": [[int(x), int(y)] for x, y in self.points],
            "n_points": len(self.points),
            "img_width": self.orig_w,
            "img_height": self.orig_h,
        }
        os.makedirs(os.path.dirname(os.path.abspath(self.out_path)), exist_ok=True)
        with open(self.out_path, "w") as f:
            json.dump(ann, f, indent=2)
        print(f"Saved {len(self.points)} point(s) to: {self.out_path}")
        self.root.destroy()

    def _quit(self):
        if self.points and not messagebox.askyesno("Quit", "Quit without saving?"):
            return
        self.root.destroy()


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------

def default_out_path(image_path):
    stem = os.path.splitext(os.path.basename(image_path))[0]
    img_dir = os.path.dirname(os.path.abspath(image_path))
    return os.path.join(img_dir, "annotations", stem + ".json")


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
