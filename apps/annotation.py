import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from dash.development.base_component import Component
from PIL import Image
from plotly.graph_objects import Figure

import custom_components
from app import app
from utilities.custom_types import AnyPath
from utilities.data import read_image
from utilities.paths import ANNOTATED_ROOT, INPUT_ROOT


def style_cursor(figure: Figure):
    """Style the cursor of a figure to allow an easy annotation.

    :param figure: Plotly figure.
    """
    crosshair_kwargs = {
        "showspikes": True,
        "spikemode": "across",
        "spikesnap": "cursor",
        "spikethickness": 0.5,
        "visible": False,
    }
    figure.update_xaxes(**crosshair_kwargs)
    figure.update_yaxes(**crosshair_kwargs)
    figure.update_traces(hoverinfo="none", hovertemplate="")


def style_annotations(figure: Figure):
    """Style the annotations of a figure.

    :param figure: Plotly figure.
    """
    figure.update_layout(
        dragmode="drawrect",
        newshape={
            "fillcolor": None,
            "opacity": 0.4,
            "line": {"color": "red", "width": 3},
        },
    )


def get_layout() -> Component:
    """Return the layout of the annotation app.

    :return: Layout of the annotation app.
    """

    image_path = get_current_image_path()

    layout = dbc.Col(
        [
            dbc.Row(
                get_graph_or_message(image_path),
                id="graph-or-message",
                className="flex-fill",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button(
                        "Save & next",
                        id="save-next",
                        n_clicks=0,
                        disabled=True,
                        className="invisible" if image_path is None else "visible",
                    ),
                    className="text-center",
                ),
            ),
            dcc.Store(id="image-path", data=str(image_path)),
        ],
        className="d-flex flex-column",
    )

    return layout


def get_graph(image_path: AnyPath) -> dcc.Graph:
    """Get a graph suitable for annotation, with an image.

    :param image_path: Path of the image.
    :return: Plotly graph.
    """
    graph_config = {
        "displaylogo": False,
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtons": [["eraseshape", "autoScale2d"]],
    }

    return dcc.Graph(
        config=graph_config,
        id="graph-annotation",
        figure=get_figure(image_path),
    )


def get_graph_or_message(image_path: Optional[AnyPath]) -> Union[dcc.Graph, Component]:
    """Get either an annotation graph or an error message, if there is no image.

    :param image_path: Path to an image. Can be `None`.
    :return: Either a plotly graph with an image or a html component showing an error message.
    """
    if image_path is None:
        return custom_components.Message(
            [
                """There are currently no files in the './data/input' folder. Either put some images that you want to 
                annotate into the folder and """,
                html.A("refresh", href="/apps/annotation"),
                " this page, or ",
                html.A("evaluate", href="/apps/evaluation"),
                " previously annotated images.",
            ]
        )
    else:
        return get_graph(image_path)


def get_figure(image_path: Optional[AnyPath]) -> Figure:
    """Get a figure showing an image, styled for annotation.

    :param image_path: Path to the image. Can be `None`.
    :return: Plotly figure that is styled for annotation, showing an image, or None, if there is no image.
    """
    if image_path is not None:
        image = read_image(image_path)
        figure = px.imshow(image)
        style_annotations(figure)
        style_cursor(figure)

        figure.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            modebar=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=20, r=20, t=40, b=20),
        )

        return figure


def get_current_image_path() -> Optional[AnyPath]:
    """Get the first image in the `input` folder.

    :return: Path of the first image in the `input` folder.
    """
    image_paths = sorted(list(INPUT_ROOT.glob("?*.*")))
    if image_paths:
        return image_paths[0]


@app.callback(
    Output("graph-or-message", "children"),
    Output("image-path", "data"),
    Output("save-next", "className"),
    Input("save-next", "n_clicks"),
    State("graph-annotation", "relayoutData"),
    State("image-path", "data"),
    prevent_initial_call=True,
)
def save_annotations_and_move_input_image(
    _, relayout_data: Optional[Dict], image_path: str
) -> Tuple[Union[dcc.Graph, Component], str, str]:
    """Save annotations as csv-file. Move csv file and image file to the `annotated` folder.

    :param _: Mandatory input for the callback. Unused.
    :param relayout_data: Dictionary, holding information about the annotations.
    :param image_path: Path of the input image.
    :return: Graph of for the annotation of the next image or message saying that there are no more images.
    """

    shapes = relayout_data.get("shapes")

    wanted_keys = ["x0", "y0", "x1", "y1"]
    annotations = pd.DataFrame(
        [dict((k, shape[k]) for k in wanted_keys if k in shape) for shape in shapes]
    )

    image_path = Path(image_path)

    image_id = image_path.stem

    if image_id.startswith("image_"):  # Catch if the image file name already has the suffix.
        image_id = image_id[6:]

    ANNOTATED_ROOT.mkdir(exist_ok=True, parents=True)

    csv_path = ANNOTATED_ROOT / f"annotation_{image_id}.csv"
    annotations.to_csv(csv_path, index=False)

    output_image_path = ANNOTATED_ROOT / f"image_{image_id}.png"
    Image.open(image_path).save(output_image_path)
    os.remove(image_path)

    image_path = get_current_image_path()

    button_class = "invisible" if image_path is None else "visible"

    # TODO: Load evaluation app, if there are no more images.
    return get_graph_or_message(image_path), str(image_path), button_class


@app.callback(
    Output("save-next", "disabled"),
    Input("graph-annotation", "relayoutData"),
)
def disable_button(relayout_data: Optional[Dict]) -> bool:
    """Check if the `Save & next` button should be activated or not. )

    :param relayout_data: Graph annotation data.
    :return: True, if the button should be activated, false, if not.
    """

    # TODO: Fix bug, where button is disabled after zooming. Maybe using an interval?

    if relayout_data is None:
        return True

    if "shapes" not in relayout_data:
        return True

    if "xaxis.range[0]" not in relayout_data:
        return False
