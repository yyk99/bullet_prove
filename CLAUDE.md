# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project goal

**Target shooting image analyzer.** The app analyzes photos of paper shooting targets, detects bullet holes, and computes shooting statistics: accuracy (deviation from aim point), precision (grouping spread/consistency), score per zone, etc.

The name "bullet_prove" is a pun on "bulletproof" — scattered dots in images represent bullet holes, and the project "proves" (detects and scores) them.

Future realism improvements for training data: concentric scoring rings, torn-paper texture, overlapping holes from close shots, varying lighting.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
make test
# equivalent to: python3 -m unittest discover

# Run a single test file
python3 -m unittest tests.tests_basic

# Run a single test method
python3 -m unittest tests.tests_basic.Test_bulletprove_Generator.test_1

# Format code
make format
# equivalent to: python3 -m pyink .

# --- ML pipeline ---

# 1. Generate labelled training data (500 images by default)
python scripts/generate_data.py --out_dir data --n_images 500

# 2. Train the detector (saves checkpoints/best_model.keras)
python scripts/train.py --data_dir data --epochs 30

# 3. Run detection on an image (Keras or TFLite model)
python scripts/detect.py path/to/image.png --output result.png
python scripts/detect.py path/to/image.png --model checkpoints/model_float16.tflite

# 4. Export to TFLite for mobile deployment
python scripts/export_tflite.py --quantize float32   # baseline
python scripts/export_tflite.py --quantize float16   # ~2x smaller, good GPU mobile
python scripts/export_tflite.py --quantize int8 --data_dir data  # ~4x smaller, fastest mobile CPU
```

## Architecture

This is a Python ML sample project. The package is named `bulletprove` (directory: `bulletprove/`).

### Core package modules

- `bulletprove/generator.py` - Original `Generator` class: generates matplotlib scatter plot PNGs.
- `bulletprove/core.py` - Placeholder, currently empty.
- `bulletprove/__init__.py` - Inserts the package directory into `sys.path` and does bare `import core` / `import generator`, so both `bulletprove.generator.Generator` and the bare name `generator.Generator` resolve. New modules are NOT auto-imported here.

### ML pipeline modules

- `bulletprove/data_gen.py` - `LabeledGenerator`: draws random dots with PIL, saves PNG images and matching JSON annotations `{"points": [[x,y],...], "img_width":..., "img_height":...}`.
- `bulletprove/dataset.py` - `ScatterDataset` (PyTorch `Dataset`): loads image+annotation pairs, scales coordinates to the target `img_size`, and converts point annotations to Gaussian density maps via `scipy.ndimage.gaussian_filter`.
- `bulletprove/model.py` - `build_scatter_detector(input_shape)`: Keras functional API U-Net (3-level encoder, bridge, 3-level decoder with skip connections). Input `(H,W,3)`, output `(H,W,1)` non-negative density map. Requires H and W divisible by 8.

### Scripts

- `scripts/generate_data.py` - Generates `data/images/` + `data/annotations/` directories.
- `scripts/train.py` - Trains with MSE loss via `model.fit()`, saves `checkpoints/best_model.keras` and `last_model.keras`.
- `scripts/detect.py` - Loads a `.keras` or `.tflite` model, runs inference, finds peaks with `scipy.ndimage.maximum_filter`, and optionally saves an annotated image. Default threshold is `0.001` — with `sigma=8` the Gaussian peak for a single point is ~0.0025, so the threshold must stay well below that.
- `scripts/export_tflite.py` - Converts a trained Keras model to TFLite. Supports `float32`, `float16`, and `int8` quantization (INT8 requires a calibration dataset).

### Data flow

```
LabeledGenerator  -->  data/images/*.png
                  -->  data/annotations/*.json
                         |
                  ScatterDataset -> tf.data.Dataset (Gaussian density maps)
                         |
                  build_scatter_detector() U-Net  [TensorFlow/Keras]
                         |
                  best_model.keras
                         |
                  export_tflite.py  -->  model_{float32|float16|int8}.tflite
                         |
                  detect.py (desktop) / TFLite runtime (mobile)
                         |
                  density map  -->  find_peaks()  -->  (x, y) detections
```

Tests are in `tests/`. `tests/context.py` inserts the repo root into `sys.path` so `import bulletprove` resolves correctly from the test directory. Test output images are written to `out/` (not tracked by git).
