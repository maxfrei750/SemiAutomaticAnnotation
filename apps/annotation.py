import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from dash.development.base_component import Component
from PIL import Image
from plotly.graph_objects import Figure

from app import app
from utilities.custom_types import AnyPath
from utilities.data import read_image
from utilities.paths import ANNOTATED_ROOT, INPUT_ROOT

from . import error_message


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

    layout = html.Div(
        [
            html.Div(
                get_graph_or_message(image_path), style={"height": "90%"}, id="graph-or-message"
            ),
            html.Center(
                html.Button(
                    "Save & next",
                    id="save-next",
                    n_clicks=0,
                    disabled=True,
                    hidden=image_path is None,
                ),
            ),
            dcc.Store(id="image-path", data=str(image_path)),
        ],
        style={"height": "100vh"},
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
        style={"height": "100%"},
    )


def get_graph_or_message(image_path: Optional[AnyPath]) -> Union[dcc.Graph, Component]:
    """Get either an annotation graph or an error message, if there is no image.

    :param image_path: Path to an image. Can be `None`.
    :return: Either a plotly graph with an image or a html component showing an error message.
    """
    if image_path is None:
        return error_message.get_layout(
            "No files in folder 'input'.", [dcc.Link("Menu", href="/apps/menu")]
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
            modebar={"bgcolor": "rgba(0,0,0,0)"},
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
    Output("save-next", "hidden"),
    Input("save-next", "n_clicks"),
    State("graph-annotation", "relayoutData"),
    State("image-path", "data"),
    prevent_initial_call=True,
)
def save_annotations_and_move_input_image(
    _, relayout_data: Optional[Dict], image_path: str
) -> Tuple[Union[dcc.Graph, Component], str, bool]:
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

    hidden = image_path is None

    return get_graph_or_message(image_path), str(image_path), hidden


@app.callback(
    Output("save-next", "disabled"),
    Input("graph-annotation", "relayoutData"),
)
def disable_button(relayout_data: Optional[Dict]) -> bool:
    """Check if the `Save & next` button should be activated or not. )

    :param relayout_data: Graph annotation data.
    :return: True, if the button should be activated, false, if not.
    """

    if relayout_data is None:
        return True

    if "shapes" not in relayout_data:
        return True

    if "xaxis.range[0]" not in relayout_data:
        return False
