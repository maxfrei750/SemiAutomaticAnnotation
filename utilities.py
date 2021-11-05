import numpy as np
import tensorflow as tf
from PIL import Image

from custom_types import AnyPath


def read_image(path: AnyPath):
    """Read an image.

    :param path: input path
    :return: image [Y, X, 3]
    """
    with tf.io.gfile.GFile(path, "rb") as f:
        image = Image.open(f).convert("RGB")
        return np.array(image, dtype=np.uint8)
