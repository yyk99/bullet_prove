#
#
#

import json
import os

import numpy as np
import tensorflow as tf
from PIL import Image
from scipy.ndimage import gaussian_filter


class ScatterDataset:
    """Loads image/annotation pairs and exposes them as a tf.data.Dataset.

    Each sample yields:
        image   – float32 (H, W, 3) normalised to [0, 1]
        density – float32 (H, W, 1) Gaussian density map
    """

    def __init__(self, img_dir, ann_dir, img_size=(256, 256), sigma=8, density_scale=100.0):
        self.img_dir = img_dir
        self.ann_dir = ann_dir
        self.img_size = img_size  # (W, H)
        self.sigma = sigma
        self.density_scale = density_scale  # multiplier to bring peak values into a range MSE can learn
        self.samples = self._collect_samples()

    def _collect_samples(self):
        samples = []
        for fname in sorted(os.listdir(self.img_dir)):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            stem = os.path.splitext(fname)[0]
            ann_path = os.path.join(self.ann_dir, stem + ".json")
            if os.path.exists(ann_path):
                samples.append((os.path.join(self.img_dir, fname), ann_path))
        return samples

    def __len__(self):
        return len(self.samples)

    def _load_sample(self, img_path, ann_path):
        """Load one (image, density_map) pair as numpy arrays."""
        W, H = self.img_size

        img = np.array(
            Image.open(img_path).convert("RGB").resize((W, H)), dtype=np.float32
        ) / 255.0  # (H, W, 3)

        with open(ann_path) as f:
            ann = json.load(f)

        orig_w = ann.get("img_width", W)
        orig_h = ann.get("img_height", H)
        scale_x = W / orig_w
        scale_y = H / orig_h

        density = np.zeros((H, W), dtype=np.float32)
        for x, y in ann["points"]:
            xi, yi = int(x * scale_x), int(y * scale_y)
            if 0 <= xi < W and 0 <= yi < H:
                density[yi, xi] += 1.0

        density = gaussian_filter(density, sigma=self.sigma) * self.density_scale
        density = density[:, :, np.newaxis]  # (H, W, 1)

        return img, density

    def as_tf_dataset(self, batch_size=16, shuffle=False, seed=42):
        """Return a batched, prefetched tf.data.Dataset."""
        W, H = self.img_size
        img_paths = [s[0] for s in self.samples]
        ann_paths = [s[1] for s in self.samples]

        def _py_load(img_path_t, ann_path_t):
            img, density = self._load_sample(
                img_path_t.numpy().decode(), ann_path_t.numpy().decode()
            )
            return img, density

        def _tf_load(img_path_t, ann_path_t):
            img, density = tf.py_function(_py_load, [img_path_t, ann_path_t], [tf.float32, tf.float32])
            img.set_shape([H, W, 3])
            density.set_shape([H, W, 1])
            return img, density

        ds = tf.data.Dataset.from_tensor_slices((img_paths, ann_paths))
        if shuffle:
            ds = ds.shuffle(len(self.samples), seed=seed)
        ds = ds.map(_tf_load, num_parallel_calls=tf.data.AUTOTUNE)
        ds = ds.batch(batch_size)
        ds = ds.prefetch(tf.data.AUTOTUNE)
        return ds
