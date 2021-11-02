import plotly.express as px
from dash import Input, Output, State, dcc, html

from app import app
from prediction import read_image

from . import error_message
from .paths import INPUT_ROOT


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
    input_image_paths = list(INPUT_ROOT.glob("*.*"))

    if input_image_paths:
        image_path = input_image_paths[0]  # only use first image
        image = read_image(image_path)
        figure = px.imshow(image)
        style_annotations(figure)
        style_cursor(figure)
        graph_config = {
            "displaylogo": False,
            "displayModeBar": True,
            "scrollZoom": True,
            "modeBarButtons": [["eraseshape", "autoScale2d"]],
        }
        layout = html.Div(
            [
                dcc.Graph(
                    figure=figure,
                    config=graph_config,
                    id="figure-annotation",
                    style={"height": "95%"},  # TODO: Make filling flexible
                ),
                html.Center(
                    html.Button("Save & next", id="save-next", n_clicks=0),
                ),
                html.Div(id="dummy"),
            ],
            style={"height": "98vh"},
        )
    else:
        layout = error_message.get_layout("No files in folder 'input'.")

    return layout


@app.callback(
    Output("dummy", "children"),
    Input("save-next", "n_clicks"),
    State("figure-annotation", "relayoutData"),
    prevent_initial_call=True,
)
def store_annotations(n_clicks, relayout_data):
    raise NotImplementedError
