#!/usr/bin/env python3
"""Export a trained Keras model to TFLite for mobile deployment.

Three quantization modes:
  float32  – no quantization, full accuracy (default)
  float16  – half-precision weights, ~2x smaller, GPU-accelerated on mobile
  int8     – integer weights + activations, ~4x smaller, fastest on mobile CPU

INT8 requires a representative dataset to calibrate activation ranges.

Usage:
    python scripts/export_tflite.py
    python scripts/export_tflite.py --quantize float16
    python scripts/export_tflite.py --quantize int8 --data_dir data
"""

import argparse
import os
import sys

import numpy as np
import tensorflow as tf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def representative_dataset(data_dir, img_size, n_samples=100):
    """Yield batches of calibration images for INT8 quantization."""
    from bulletprove.dataset import ScatterDataset

    ds = ScatterDataset(
        img_dir=os.path.join(data_dir, "images"),
        ann_dir=os.path.join(data_dir, "annotations"),
        img_size=(img_size, img_size),
    )
    samples = ds.samples[:n_samples]
    for img_path, _ in samples:
        img = np.array(
            __import__("PIL").Image.open(img_path).convert("RGB").resize((img_size, img_size)),
            dtype=np.float32,
        ) / 255.0
        yield [img[np.newaxis]]  # (1, H, W, 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="checkpoints/best_model.keras")
    parser.add_argument("--output_dir", default="checkpoints")
    parser.add_argument(
        "--quantize",
        choices=["float32", "float16", "int8"],
        default="float32",
        help="Quantization mode",
    )
    parser.add_argument("--img_size", type=int, default=256)
    parser.add_argument("--data_dir", default="data", help="Required for int8 calibration")
    args = parser.parse_args()

    if not os.path.exists(args.model):
        sys.exit(f"Model not found: {args.model}\nRun scripts/train.py first.")

    print(f"Loading model: {args.model}")
    model = tf.keras.models.load_model(args.model)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if args.quantize == "float16":
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]

    elif args.quantize == "int8":
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = lambda: representative_dataset(
            args.data_dir, args.img_size
        )
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.uint8
        converter.inference_output_type = tf.uint8

    print(f"Converting with quantization: {args.quantize} ...")
    tflite_model = converter.convert()

    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, f"model_{args.quantize}.tflite")
    with open(out_path, "wb") as f:
        f.write(tflite_model)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"Saved: {out_path}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
