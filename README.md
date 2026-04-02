# bullet_prove

Analyzes target shooting images, detects bullet holes, and computes accuracy/precision statistics.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## ML pipeline

### 1. Generate training data

Creates synthetic images of scattered dots (simulating bullet holes) with ground-truth annotations.

```bash
python scripts/generate_data.py
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--out_dir` | `data` | Output directory |
| `--n_images` | `500` | Number of images to generate |
| `--n_min` / `--n_max` | `3` / `20` | Dot count range per image |
| `--img_size` | `256` | Image width and height in pixels |

Output: `data/images/*.png` and `data/annotations/*.json`.

### 2. Train the detector

```bash
python scripts/train.py
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--data_dir` | `data` | Directory with `images/` and `annotations/` |
| `--checkpoint_dir` | `checkpoints` | Where to save model files |
| `--epochs` | `30` | Training epochs |
| `--batch_size` | `16` | Batch size |
| `--sigma` | `8` | Gaussian radius for density map labels |

Output: `checkpoints/best_model.keras` and `checkpoints/last_model.keras`.

### 3. Detect objects in an image

```bash
python scripts/detect.py path/to/image.png --output result.png
```

Key options:

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `checkpoints/best_model.keras` | Keras or TFLite model path |
| `--threshold` | `0.1` | Minimum density score to count as a detection |
| `--min_distance` | `15` | Minimum pixel distance between detections |
| `--output` | _(display)_ | Save annotated image to this path |

### 4. Export to TFLite (mobile deployment)

```bash
# Full precision (baseline)
python scripts/export_tflite.py --quantize float32

# Half precision — ~2x smaller, good for mobile GPU
python scripts/export_tflite.py --quantize float16

# Integer quantization — ~4x smaller, fastest on mobile CPU
python scripts/export_tflite.py --quantize int8 --data_dir data
```

Output: `checkpoints/model_{float32|float16|int8}.tflite`.

## Running tests

```bash
make test
```

## Code formatting

```bash
make format
```
