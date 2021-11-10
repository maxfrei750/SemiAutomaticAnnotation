import os
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from PIL import Image

from app import app
from custom_types import AnyPath
from utilities import read_image

from . import error_message
from .paths import ANNOTATED_ROOT, INPUT_ROOT


def style_cursor(figure):
    # Style cursor
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


def style_annotations(figure):
    # Style annotation
    figure.update_layout(
        dragmode="drawrect",
        newshape={
            "fillcolor": None,
            "opacity": 0.4,
            "line": {"color": "red", "width": 3},
        },
    )


def get_layout():

    image_path = str(get_current_image_path())

    layout = html.Div(
        [
            html.Div(get_graph(image_path), style={"height": "90%"}, id="graph-or-message"),
            html.Center(
                html.Button("Save & next", id="save-next", n_clicks=0, disabled=True),
            ),
            dcc.Store(id="image-path", data=str(image_path)),
        ],
        style={"height": "100vh"},
    )

    return layout


def get_graph(image_path):
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


def get_graph_or_message(image_path):
    if image_path is None:
        return error_message.get_layout(
            "No files in folder 'input'.", [dcc.Link("Evaluation", href="/apps/evaluation")]
        )
    else:
        return get_graph(image_path)


def get_figure(image_path: AnyPath):
    if image_path is not None:
        image = read_image(image_path)
        figure = px.imshow(image)
        style_annotations(figure)
        style_cursor(figure)

        return figure


def get_current_image_path() -> Optional[AnyPath]:
    image_paths = sorted(list(INPUT_ROOT.glob("*.*")))
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
def save_annotations_and_move_input_image(_, relayout_data, image_path):

    shapes = relayout_data.get("shapes")

    wanted_keys = ["x0", "y0", "x1", "y1"]
    annotations = pd.DataFrame(
        [dict((k, shape[k]) for k in wanted_keys if k in shape) for shape in shapes]
    )

    image_path = Path(image_path)

    image_id = image_path.stem

    if image_id.startswith("image_"):  # Catch if the image file name already has the suffix.
        image_id = image_id[6:]

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
def disable_button(relayout_data):

    if relayout_data is None:
        return True

    if "shapes" not in relayout_data:
        return True

    if "xaxis.range[0]" not in relayout_data:
        return False
