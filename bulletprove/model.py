#
#
#

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def _double_conv(x, filters, name):
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False, name=f"{name}_c1")(x)
    x = layers.BatchNormalization(name=f"{name}_bn1")(x)
    x = layers.ReLU(name=f"{name}_relu1")(x)
    x = layers.Conv2D(filters, 3, padding="same", use_bias=False, name=f"{name}_c2")(x)
    x = layers.BatchNormalization(name=f"{name}_bn2")(x)
    x = layers.ReLU(name=f"{name}_relu2")(x)
    return x


def build_scatter_detector(input_shape=(256, 256, 3)):
    """Build a lightweight U-Net that outputs a per-pixel density map.

    Input:  (H, W, 3)  – RGB image normalised to [0, 1]
    Output: (H, W, 1)  – non-negative density map; local peaks = object centres

    H and W must be divisible by 8.
    """
    inp = keras.Input(shape=input_shape, name="image")

    # Encoder
    e1 = _double_conv(inp, 32, "enc1")                          # (H,   W,   32)
    e2 = _double_conv(layers.MaxPooling2D(2)(e1), 64, "enc2")   # (H/2, W/2, 64)
    e3 = _double_conv(layers.MaxPooling2D(2)(e2), 128, "enc3")  # (H/4, W/4, 128)

    # Bridge
    b = _double_conv(layers.MaxPooling2D(2)(e3), 256, "bridge") # (H/8, W/8, 256)

    # Decoder with skip connections
    d3 = layers.Concatenate()([layers.Conv2DTranspose(128, 2, strides=2, name="up3")(b), e3])
    d3 = _double_conv(d3, 128, "dec3")

    d2 = layers.Concatenate()([layers.Conv2DTranspose(64, 2, strides=2, name="up2")(d3), e2])
    d2 = _double_conv(d2, 64, "dec2")

    d1 = layers.Concatenate()([layers.Conv2DTranspose(32, 2, strides=2, name="up1")(d2), e1])
    d1 = _double_conv(d1, 32, "dec1")

    # Output head – ReLU ensures non-negative density values
    out = layers.Conv2D(1, 1, activation="relu", name="density")(d1)

    return keras.Model(inputs=inp, outputs=out, name="ScatterDetector")
