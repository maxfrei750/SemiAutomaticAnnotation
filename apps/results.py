import base64

import dash_bootstrap_components as dbc
from dash import dcc, html

from apps import error_message

from .paths import OUTPUT_ROOT

# TODO: Type annotations.
# TODO: Documentation.


def gather_image_paths():
    return sorted(list(OUTPUT_ROOT.glob("visualization_*.*")))


def b64_image(image_filename):
    with open(image_filename, "rb") as f:
        image = f.read()
    return "data:image/png;base64," + base64.b64encode(image).decode("utf-8")


def get_layout():
    image_paths = gather_image_paths()

    # TODO: Use bootstrap layout to have a correct aspect ration etc.

    if image_paths:
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
            for image_id, image_path in enumerate(image_paths)
        ]

        layout = html.Div(
            dbc.Carousel(items=carousel_items, controls=True, indicators=True),
        )

    else:
        layout = error_message.get_layout(
            "There are no results yet.", [dcc.Link("Menu", href="/apps/menu")]
        )

    return layout
