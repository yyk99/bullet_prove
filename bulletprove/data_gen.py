#
#
#

import json
import os

import numpy as np
from PIL import Image, ImageDraw


class LabeledGenerator:
    """Generates scatter images with known dot positions saved as JSON annotations."""

    def __init__(self, img_width=256, img_height=256, dot_radius=6):
        self.img_width = img_width
        self.img_height = img_height
        self.dot_radius = dot_radius

    def generate(self, img_path, ann_path, n_points=None, n_min=3, n_max=20):
        """Generate one image and its annotation file.

        Args:
            img_path: Path to save the PNG image.
            ann_path: Path to save the JSON annotation.
            n_points: Exact dot count; if None, sampled uniformly in [n_min, n_max].
            n_min: Minimum dots (used when n_points is None).
            n_max: Maximum dots (used when n_points is None).

        Returns:
            List of (x, y) pixel coordinates of each dot.
        """
        if n_points is None:
            n_points = np.random.randint(n_min, n_max + 1)

        margin = self.dot_radius + 4
        cx = np.random.randint(margin, self.img_width - margin, n_points)
        cy = np.random.randint(margin, self.img_height - margin, n_points)

        # Noisy light-grey background
        bg = np.random.randint(220, 256, (self.img_height, self.img_width, 3), dtype=np.uint8)
        img = Image.fromarray(bg)
        draw = ImageDraw.Draw(img)

        for x, y in zip(cx, cy):
            r = self.dot_radius
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(20, 20, 20))

        os.makedirs(os.path.dirname(os.path.abspath(img_path)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(ann_path)), exist_ok=True)
        img.save(img_path)

        points = list(zip(cx.tolist(), cy.tolist()))
        with open(ann_path, "w") as f:
            json.dump(
                {
                    "points": points,
                    "n_points": n_points,
                    "img_width": self.img_width,
                    "img_height": self.img_height,
                },
                f,
            )

        return points
