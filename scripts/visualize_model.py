#!/usr/bin/env python3
"""Generate a diagram of the ScatterDetector U-Net architecture.

Usage:
    python scripts/visualize_model.py
    python scripts/visualize_model.py --output docs/architecture.png --dpi 200
"""

import argparse
import os
import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_block(ax, cx, cy, w, h, title, shape, color):
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.08",
        facecolor=color, edgecolor="#333333", linewidth=1.5, zorder=3,
    )
    ax.add_patch(rect)
    ax.text(cx, cy + 0.14, title,
            ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)
    ax.text(cx, cy - 0.18, shape,
            ha="center", va="center", fontsize=7.5, color="#444444", zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, color="#333333", lw=1.5, dashed=False):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->",
            color=color,
            lw=lw,
            linestyle="dashed" if dashed else "solid",
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=2,
    )


def draw_label(ax, x, y, text, color="#333333", fontsize=7, ha="left"):
    ax.text(x, y, text, ha=ha, va="center", fontsize=fontsize, color=color)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="net_structure.png")
    parser.add_argument("--dpi", type=int, default=150)
    args = parser.parse_args()

    CW, CH = 20, 12   # canvas width / height in data units
    fig, ax = plt.subplots(figsize=(CW * 0.75, CH * 0.75))
    ax.set_xlim(0, CW)
    ax.set_ylim(0, CH)
    ax.axis("off")
    fig.patch.set_facecolor("#F5F6FA")
    ax.set_facecolor("#F5F6FA")
    ax.set_title("ScatterDetector – U-Net Architecture",
                 fontsize=14, fontweight="bold", pad=16)

    # Colour palette
    C_IN  = "#FAD7A0"   # input / output
    C_ENC = "#AED6F1"   # encoder
    C_BRG = "#D2B4DE"   # bridge
    C_DEC = "#A9DFBF"   # decoder

    BW = 2.8   # block width
    BH = 0.85  # block height
    EX = 3.0   # encoder column x
    DX = 17.0  # decoder column x
    BX = 10.0  # bridge x

    # Y levels – same y == same spatial resolution
    YI  = 11.0   # input / output   (no pooling yet)
    Y1  =  9.2   # 256 × 256
    Y2  =  7.4   # 128 × 128
    Y3  =  5.6   # 64  × 64
    YB  =  3.6   # 32  × 32  (bridge)

    # ---- Blocks -------------------------------------------------------
    draw_block(ax, EX, YI, BW, BH, "Input",      "256 × 256 × 3",   C_IN)
    draw_block(ax, EX, Y1, BW, BH, "Encoder 1",  "256 × 256 × 32",  C_ENC)
    draw_block(ax, EX, Y2, BW, BH, "Encoder 2",  "128 × 128 × 64",  C_ENC)
    draw_block(ax, EX, Y3, BW, BH, "Encoder 3",  "64 × 64 × 128",   C_ENC)
    draw_block(ax, BX, YB, BW, BH, "Bridge",     "32 × 32 × 256",   C_BRG)
    draw_block(ax, DX, Y3, BW, BH, "Decoder 3",  "64 × 64 × 128",   C_DEC)
    draw_block(ax, DX, Y2, BW, BH, "Decoder 2",  "128 × 128 × 64",  C_DEC)
    draw_block(ax, DX, Y1, BW, BH, "Decoder 1",  "256 × 256 × 32",  C_DEC)
    draw_block(ax, DX, YI, BW, BH, "Output",     "256 × 256 × 1",   C_IN)

    # Sub-label: operation inside each block
    for cx, cy in [(EX, Y1), (EX, Y2), (EX, Y3),
                   (BX, YB),
                   (DX, Y3), (DX, Y2), (DX, Y1)]:
        ax.text(cx, cy - 0.40, "2 × (Conv 3×3 → BN → ReLU)",
                ha="center", va="center", fontsize=6, color="#666666",
                style="italic", zorder=4)

    # ---- Encoder path -------------------------------------------------
    ENC_COLOR = "#1A5276"

    # Input → Enc1
    draw_arrow(ax, EX, YI - BH / 2, EX, Y1 + BH / 2, color=ENC_COLOR)

    # Enc1 → Enc2  (MaxPool)
    draw_arrow(ax, EX, Y1 - BH / 2, EX, Y2 + BH / 2, color=ENC_COLOR)
    draw_label(ax, EX + 0.12, (Y1 + Y2) / 2, "MaxPool ÷2", color=ENC_COLOR)

    # Enc2 → Enc3  (MaxPool)
    draw_arrow(ax, EX, Y2 - BH / 2, EX, Y3 + BH / 2, color=ENC_COLOR)
    draw_label(ax, EX + 0.12, (Y2 + Y3) / 2, "MaxPool ÷2", color=ENC_COLOR)

    # Enc3 → Bridge  (MaxPool, diagonal)
    draw_arrow(ax, EX + BW / 2, Y3, BX - BW / 2, YB, color=ENC_COLOR)
    draw_label(ax, (EX + BW / 2 + BX - BW / 2) / 2 - 1.2,
               (Y3 + YB) / 2 - 0.1, "MaxPool ÷2", color=ENC_COLOR, ha="center")

    # ---- Decoder path -------------------------------------------------
    DEC_COLOR = "#1D6A39"

    # Bridge → Dec3  (Upsample, diagonal)
    draw_arrow(ax, BX + BW / 2, YB, DX - BW / 2, Y3, color=DEC_COLOR)
    draw_label(ax, (BX + BW / 2 + DX - BW / 2) / 2 - 0.5,
               (YB + Y3) / 2 - 0.1, "Upsample ×2", color=DEC_COLOR, ha="center")

    # Dec3 → Dec2  (Upsample)
    draw_arrow(ax, DX, Y3 + BH / 2, DX, Y2 - BH / 2, color=DEC_COLOR)
    draw_label(ax, DX + 0.12, (Y3 + Y2) / 2, "Upsample ×2", color=DEC_COLOR)

    # Dec2 → Dec1  (Upsample)
    draw_arrow(ax, DX, Y2 + BH / 2, DX, Y1 - BH / 2, color=DEC_COLOR)
    draw_label(ax, DX + 0.12, (Y2 + Y1) / 2, "Upsample ×2", color=DEC_COLOR)

    # Dec1 → Output
    draw_arrow(ax, DX, Y1 + BH / 2, DX, YI - BH / 2, color=DEC_COLOR)
    draw_label(ax, DX + 0.12, (Y1 + YI) / 2, "Conv 1×1 → ReLU", color=DEC_COLOR)

    # ---- Skip connections ---------------------------------------------
    SKIP_COLOR = "#C0392B"
    for y, label in [
        (Y1, "concat  (32 + 32 → 64 ch)"),
        (Y2, "concat  (64 + 64 → 128 ch)"),
        (Y3, "concat  (128 + 128 → 256 ch)"),
    ]:
        x1 = EX + BW / 2 + 0.1
        x2 = DX - BW / 2 - 0.1
        draw_arrow(ax, x1, y, x2, y, color=SKIP_COLOR, lw=1.5, dashed=True)
        ax.text((x1 + x2) / 2, y + 0.28, label,
                ha="center", va="bottom", fontsize=7,
                color=SKIP_COLOR, style="italic")

    # ---- Legend -------------------------------------------------------
    lx, ly = 0.25, 6.0
    ax.text(lx, ly + 0.3, "Legend", fontsize=9, fontweight="bold")

    legend_items = [
        (C_ENC, "Encoder block"),
        (C_BRG, "Bridge"),
        (C_DEC, "Decoder block"),
        (C_IN,  "Input / Output"),
    ]
    for i, (color, label) in enumerate(legend_items):
        ry = ly - 0.10 - i * 0.60
        rect = mpatches.FancyBboxPatch(
            (lx, ry - 0.18), 0.45, 0.36,
            boxstyle="round,pad=0.04",
            facecolor=color, edgecolor="#333333", linewidth=1,
        )
        ax.add_patch(rect)
        ax.text(lx + 0.60, ry, label, va="center", fontsize=8)

    # Skip connection in legend
    skip_y = ly - 0.10 - len(legend_items) * 0.60
    ax.annotate("", xy=(lx + 0.45, skip_y), xytext=(lx, skip_y),
                arrowprops=dict(
                    arrowstyle="->", color=SKIP_COLOR, lw=1.5, linestyle="dashed"
                ))
    ax.text(lx + 0.60, skip_y, "Skip connection (concat)", va="center", fontsize=8)

    # Footnote
    ax.text(CW / 2, 0.4,
            "Each encoder/decoder block = 2 × (Conv 3×3 → BatchNorm → ReLU)",
            ha="center", va="center", fontsize=8, color="#555555", style="italic")

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    plt.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
    print(f"Saved: {args.output}")
    plt.close()


if __name__ == "__main__":
    main()
