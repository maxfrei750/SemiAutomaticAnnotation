import base64
from typing import List

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.development.base_component import Component

import custom_components
from utilities.custom_types import AnyPath
from utilities.paths import RESULTS_ROOT, ROOT


def gather_visualization_paths() -> List[AnyPath]:
    """Gather paths of visualization images.

    :return: List of paths of visualization images.
    """
    return sorted(list(RESULTS_ROOT.glob("visualization_*.*")))


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

    if visualization_paths:
        carousel_items = [
            {
                "key": str(image_id),
                "src": b64_image(image_path),
                "img_style": {
                    "max-width": "80%",
                    "height": "80vh",
                    "object-fit": "contain",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    "margin-bottom": "5%",
                },
            }
            for image_id, image_path in enumerate(visualization_paths)
        ]

        layout = dbc.Col(
            dbc.Carousel(
                items=carousel_items,
                controls=True,
                indicators=True,
                style={"height": "100%"},
            ),
            className="d-flex flex-column",
            style={"margin-top": "2%"},
            # TODO: Add re-annotate button.
        )

    else:
        layout = custom_components.Message(
            dcc.Markdown(
                f"There are currently no results in the `./{RESULTS_ROOT.relative_to(ROOT.parent)}` folder. Please "
                f"**[annotate](/apps/annotation)** and/or **[evaluate](/apps/evaluation)** some images."
            )
        )

    return layout
