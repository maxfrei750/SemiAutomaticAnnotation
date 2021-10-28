import logging
import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from skimage import color
from skimage.color import rgb_colors

from prediction import predict_masks, read_image

COLORS = [
    rgb_colors.cyan,
    rgb_colors.orange,
    rgb_colors.pink,
    rgb_colors.purple,
    rgb_colors.limegreen,
    rgb_colors.crimson,
] + [(color) for (name, color) in color.color_dict.items()]
random.shuffle(COLORS)

logging.disable(logging.WARNING)


def plot_image_annotations(image, boxes, masks, darken_image=0.5):
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_axis_off()
    image = (image * darken_image).astype(np.uint8)
    ax.imshow(image)

    height, width, _ = image.shape

    num_colors = len(COLORS)
    color_index = 0

    for box, mask in zip(boxes, masks):
        ymin, xmin, ymax, xmax = box
        ymin *= height
        ymax *= height
        xmin *= width
        xmax *= width

        color = COLORS[color_index]
        color = np.array(color)
        rect = patches.Rectangle(
            (xmin, ymin), xmax - xmin, ymax - ymin, linewidth=2.5, edgecolor=color, facecolor="none"
        )
        ax.add_patch(rect)
        mask = (mask > 0.5).astype(np.float32)
        color_image = np.ones_like(image) * color[np.newaxis, np.newaxis, :]
        color_and_mask = np.concatenate([color_image, mask[:, :, np.newaxis]], axis=2)

        ax.imshow(color_and_mask, alpha=0.5)

        color_index = (color_index + 1) % num_colors

    return ax


def test_api():

    image_path = "/home/tensorflow/input/image3.jpg"

    image = read_image(image_path)

    boxes = np.array(
        [
            [0.000, 0.160, 0.362, 0.812],
            [0.340, 0.286, 0.472, 0.619],
            [0.437, 0.008, 0.650, 0.263],
            [0.382, 0.003, 0.538, 0.594],
            [0.518, 0.444, 0.625, 0.554],
        ]
    )

    masks = predict_masks(image, boxes)

    plot_image_annotations(image, boxes, masks)
    plt.savefig("output/test.png")


if __name__ == "__main__":
    test_api()
