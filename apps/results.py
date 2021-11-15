import base64
from typing import List

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.development.base_component import Component

from apps import error_message
from custom_types import AnyPath

from .paths import OUTPUT_ROOT


def gather_visualization_paths() -> List[AnyPath]:
    """Gather paths of visualization images.

    :return: List of paths of visualization images.
    """
    return sorted(list(OUTPUT_ROOT.glob("visualization_*.*")))


def b64_image(image_path: AnyPath) -> str:
    """Read an image and encode it as base64.

    :param image_path: path to an image
    :return: Image, encoded as base64.
    """
    with open(image_path, "rb") as f:
        image = f.read()
    return "data:image/png;base64," + base64.b64encode(image).decode("utf-8")


def get_layout() -> Component:
    """Get the layout of the results app.

    :return: Layout of the results app.
    """
    visualization_paths = gather_visualization_paths()

    # TODO: Use bootstrap layout to have a correct aspect ration etc.

    if visualization_paths:
        carousel_items = [
            {
                "key": str(image_id),
                "src": b64_image(image_path),
                "img_style": {
                    "max-width": "80%",
                    "max-height": "90vh",
                    "height": "auto",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    "margin-bottom": "10vh",
                },
            }
            for image_id, image_path in enumerate(visualization_paths)
        ]

        layout = html.Div(
            dbc.Carousel(items=carousel_items, controls=True, indicators=True),
        )

    else:
        layout = error_message.get_layout(
            "There are no results yet.", [dcc.Link("Menu", href="/apps/menu")]
        )

    return layout
