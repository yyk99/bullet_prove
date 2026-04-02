#!/usr/bin/env python3
"""Train the ScatterDetector on a labelled image dataset.

Usage:
    python scripts/train.py
    python scripts/train.py --data_dir data --epochs 50 --batch_size 16
"""

import argparse
import os
import random
import sys

import tensorflow as tf

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bulletprove.dataset import ScatterDataset
from bulletprove.model import build_scatter_detector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data_dir", default="data")
    parser.add_argument("--checkpoint_dir", default="checkpoints")
    parser.add_argument("--img_size", type=int, default=256, help="Must be divisible by 8")
    parser.add_argument("--sigma", type=int, default=5, help="Gaussian sigma for density maps")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    # Load all samples and shuffle before splitting
    full = ScatterDataset(
        img_dir=os.path.join(args.data_dir, "images"),
        ann_dir=os.path.join(args.data_dir, "annotations"),
        img_size=(args.img_size, args.img_size),
        sigma=args.sigma,
    )
    if len(full) == 0:
        sys.exit(
            f"No image/annotation pairs found in {args.data_dir}. "
            "Run scripts/generate_data.py first."
        )

    samples = full.samples[:]
    random.seed(42)
    random.shuffle(samples)

    val_size = max(1, int(0.1 * len(samples)))
    train_samples = samples[val_size:]
    val_samples = samples[:val_size]
    print(f"Dataset: {len(samples)} total  |  train={len(train_samples)}  val={len(val_samples)}")

    # Build two separate dataset views sharing the same config
    def make_ds(sample_list, shuffle):
        ds = ScatterDataset(
            img_dir=os.path.join(args.data_dir, "images"),
            ann_dir=os.path.join(args.data_dir, "annotations"),
            img_size=(args.img_size, args.img_size),
            sigma=args.sigma,
        )
        ds.samples = sample_list
        return ds.as_tf_dataset(batch_size=args.batch_size, shuffle=shuffle)

    train_ds = make_ds(train_samples, shuffle=True)
    val_ds = make_ds(val_samples, shuffle=False)

    os.makedirs(args.checkpoint_dir, exist_ok=True)
    model = build_scatter_detector(input_shape=(args.img_size, args.img_size, 3))
    model.summary(line_length=80)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.lr),
        loss="mse",
    )

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(args.checkpoint_dir, "best_model.keras"),
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, verbose=1
        ),
    ]

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )

    model.save(os.path.join(args.checkpoint_dir, "last_model.keras"))
    print(f"\nCheckpoints saved to: {args.checkpoint_dir}/")


if __name__ == "__main__":
    main()
