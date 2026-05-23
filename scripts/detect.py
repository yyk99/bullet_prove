#!/usr/bin/env python3
"""Detect scattered objects in an image using a trained ScatterDetector.

Supports both full Keras models (.keras) and TFLite models (.tflite).

Usage:
    python scripts/detect.py path/to/image.png
    python scripts/detect.py path/to/image.png --model checkpoints/model.tflite --output result.png
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def find_peaks(density, threshold, min_distance):
    """Return list of (x, y, score) for each local maximum above threshold."""
    from scipy.ndimage import label, maximum_filter

    local_max = maximum_filter(density, size=2 * min_distance + 1)
    mask = (density == local_max) & (density > threshold)
    labeled, n = label(mask)

    peaks = []
    for i in range(1, n + 1):
        ys, xs = np.where(labeled == i)
        cy, cx = int(ys.mean()), int(xs.mean())
        peaks.append((cx, cy, float(density[cy, cx])))

    peaks.sort(key=lambda p: -p[2])
    return peaks


def run_keras(model_path, img_array):
    import tensorflow as tf
    model = tf.keras.models.load_model(model_path)
    inp = img_array[np.newaxis]  # (1, H, W, 3)
    density = model.predict(inp, verbose=0)[0, :, :, 0]  # (H, W)
    return density


def run_tflite(model_path, img_array):
    import tensorflow as tf
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    in_det = interpreter.get_input_details()[0]
    out_det = interpreter.get_output_details()[0]

    inp = img_array[np.newaxis].astype(in_det["dtype"])  # (1, H, W, 3)
    interpreter.set_tensor(in_det["index"], inp)
    interpreter.invoke()
    density = interpreter.get_tensor(out_det["index"])[0, :, :, 0]  # (H, W)
    return density


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Input image path")
    parser.add_argument("--model", default="checkpoints/best_model.keras", help="Keras or TFLite model path")
    parser.add_argument("--img_size", type=int, default=256, help="Resize input before inference")
    parser.add_argument("--threshold", type=float, default=0.3, help="Minimum density score")
    parser.add_argument("--min_distance", type=int, default=20, help="Min px distance between detections")
    parser.add_argument("--output", help="Save annotated image here (omit to display)")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        sys.exit(f"Model not found: {args.model}\nRun scripts/train.py first.")

    img = Image.open(args.image).convert("RGB")
    orig_w, orig_h = img.size
    img_resized = img.resize((args.img_size, args.img_size))
    img_array = np.array(img_resized, dtype=np.float32) / 255.0  # (H, W, 3)

    if args.model.endswith(".tflite"):
        density = run_tflite(args.model, img_array)
    else:
        density = run_keras(args.model, img_array)

    print(f"Density map: min={density.min():.6f}  max={density.max():.6f}  mean={density.mean():.6f}")

    peaks = find_peaks(density, threshold=args.threshold, min_distance=args.min_distance)
    print(f"Detected {len(peaks)} object(s):")

    scale_x = orig_w / args.img_size
    scale_y = orig_h / args.img_size

    result = img.copy()
    draw = ImageDraw.Draw(result)
    r = max(8, int(12 * min(scale_x, scale_y)))

    for i, (cx, cy, score) in enumerate(peaks):
        x, y = int(cx * scale_x), int(cy * scale_y)
        print(f"  [{i + 1:3d}]  x={x:4d}  y={y:4d}  score={score:.4f}")
        draw.ellipse([x - r, y - r, x + r, y + r], outline=(255, 30, 30), width=2)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        result.save(args.output)
        print(f"\nAnnotated image saved to: {args.output}")
    else:
        result.show()


if __name__ == "__main__":
    main()
