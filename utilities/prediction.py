import json
import os

import numpy as np
import pandas as pd
import requests
import tensorflow as tf

from .data import sort_box_coordinates
from .ops import reframe_box_masks_to_image_masks

MODEL_HOST = os.environ["MODEL_HOST"]
PORT_BACKEND = os.environ["PORT_BACKEND"]


def predict_masks(image: np.ndarray, boxes: pd.DataFrame, model_name: str) -> np.ndarray:
    """Predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: pandas dataframe with columns ["y0", "x0", "y1", "x1"]
    :param model_name: name of the model to use for the evaluation.
        Either "deepmarc" or "deepmac".
    :return: instance masks [N, Y, X]
    """

    model_name = model_name

    image_height, image_width, _ = image.shape

    boxes = boxes.copy()

    # Normalize boxes.
    boxes["x0"] /= image_width
    boxes["y0"] /= image_height
    boxes["x1"] /= image_width
    boxes["y1"] /= image_height

    # Reorder coordinates.
    boxes = boxes[["y0", "x0", "y1", "x1"]]

    # Remove points outside of the image.
    boxes[boxes < 0] = 0
    boxes[boxes > 1] = 1

    sort_box_coordinates(boxes)

    boxes_numpy = boxes.to_numpy().astype(np.float32)

    if model_name == "deepmarc":
        masks = get_deepmarc_response(image, boxes_numpy)
    elif model_name == "deepmac":
        masks = get_deepmac_response(image, boxes_numpy)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    masks = reframe_box_masks_to_image_masks(
        tf.convert_to_tensor(masks),
        tf.convert_to_tensor(boxes_numpy),
        image_height,
        image_width,
    )
    return masks.numpy()


def get_deepmarc_response(image: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Use Deep-MARC to predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: boxes [N, 4]
    :return: instance masks [N, Y, X]
    """

    inference_url = f"http://{MODEL_HOST}:{PORT_BACKEND}/v1/models/deepmarc:predict"

    boxes_numpy = np.expand_dims(boxes, axis=0)
    images_numpy = np.expand_dims(image, axis=0)

    data = json.dumps(
        {
            "signature_name": "serving_default",
            "inputs": {
                "images": images_numpy.tolist(),
                "boxes": boxes_numpy.tolist(),
            },
        }
    )
    headers = {"content-type": "application/json"}
    response = requests.post(inference_url, data=data, headers=headers).json()

    masks = np.array(response["outputs"])[0, :]
    return masks


def get_deepmac_response(image: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    """Use Deep-MAC to predict instance masks for an image and a given set of boxes.

    :param image: input image [Y,X,3]
    :param boxes: boxes [N, 4]
    :return: instance masks [N, Y, X]
    """

    inference_url = f"http://{MODEL_HOST}:{PORT_BACKEND}/v1/models/deepmac:predict"

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
    return masks
