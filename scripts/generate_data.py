#!/usr/bin/env python3
"""Generate a labelled training dataset of scattered-dot images.

Usage:
    python scripts/generate_data.py
    python scripts/generate_data.py --n_images 1000 --out_dir data --n_min 2 --n_max 25
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bulletprove.data_gen import LabeledGenerator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n_images", type=int, default=500, help="Number of images to generate")
    parser.add_argument("--out_dir", default="data", help="Root output directory")
    parser.add_argument("--img_size", type=int, default=256, help="Image width and height in pixels")
    parser.add_argument("--dot_radius", type=int, default=6, help="Dot radius in pixels")
    parser.add_argument("--n_min", type=int, default=3, help="Min dots per image")
    parser.add_argument("--n_max", type=int, default=20, help="Max dots per image")
    args = parser.parse_args()

    img_dir = os.path.join(args.out_dir, "images")
    ann_dir = os.path.join(args.out_dir, "annotations")

    gen = LabeledGenerator(
        img_width=args.img_size,
        img_height=args.img_size,
        dot_radius=args.dot_radius,
    )

    for i in range(args.n_images):
        gen.generate(
            img_path=os.path.join(img_dir, f"{i:05d}.png"),
            ann_path=os.path.join(ann_dir, f"{i:05d}.json"),
            n_min=args.n_min,
            n_max=args.n_max,
        )
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{args.n_images}")

    print(f"Done. {args.n_images} images -> {img_dir}")
    print(f"      {args.n_images} annotations -> {ann_dir}")


if __name__ == "__main__":
    main()
