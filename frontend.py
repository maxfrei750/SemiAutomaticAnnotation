import os

import dash
import plotly.express as px
import plotly.io as pio
from dash import Input, Output, State, dcc, html

from prediction import read_image

pio.templates.default = "plotly_white"

PORT_FRONTEND = int(os.environ["PORT_FRONTEND"])


def main():
    image_path = "/home/tensorflow/input/image3.jpg"
    image = read_image(image_path)

    figure = px.imshow(image)

    style_annotations(figure)
    style_cursor(figure)

    app = dash.Dash(__name__)

    graph_config = {
        "displaylogo": False,
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtons": [["eraseshape", "autoScale2d"]],
    }

    app.layout = html.Div(
        [
            dcc.Graph(figure=figure, config=graph_config, style={"height": "95%"}),
            html.Center(html.Button("Submit", id="submit-button")),
        ],
        style={"height": "98vh"},
    )

    # @app.callback(Input("submit-button", "n_clicks"))
    # def update_output(n_clicks, value):
    #     print(
    #         'The input value was "{}" and the button has been clicked {} times'.format(value, n_clicks)
    #     )
    #

    app.run_server(host="0.0.0.0", port=PORT_FRONTEND, debug=True, dev_tools_ui=False)


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
        newshape={"fillcolor": None, "opacity": 1.0, "line": {"color": "red", "width": 3}},
    )


if __name__ == "__main__":
    main()
