import json
import os

import numpy as np
import requests
import tensorflow as tf
from object_detection.utils import ops
from PIL import Image

from custom_types import AnyPath


def read_image(path: AnyPath):
    """Read an image.

    :param path: input path
    :return: image [Y, X, 3]
    """
    with tf.io.gfile.GFile(path, "rb") as f:
        image = Image.open(f)
        return np.array(image, dtype=np.uint8)


def predict_masks(image: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: bounding boxes [N, 4]
    :return: instance masks [N, Y, X]
    """

    boxes = boxes.astype(np.float32)
    height, width, _ = image.shape
    inference_url = os.environ["MODEL_API_URL"]
    data = json.dumps(
        {
            "signature_name": "serving_default",
            "instances": [
                {
                    "input_tensor": image.tolist(),
                    "boxes": boxes.tolist(),
                }
            ],
        }
    )
    headers = {"content-type": "application/json"}
    response = requests.post(inference_url, data=data, headers=headers)
    masks = response.json()["predictions"][0]["detection_masks"]
    masks = ops.reframe_box_masks_to_image_masks(
        tf.convert_to_tensor(masks), tf.convert_to_tensor(boxes), height, width
    )
    return masks.numpy()
