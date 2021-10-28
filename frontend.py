import os

import dash
import plotly.express as px
import plotly.io as pio
from dash import dcc, html

from prediction import read_image

pio.templates.default = "plotly_white"

image_path = "/home/tensorflow/input/image3.jpg"
image = read_image(image_path)

fig = px.imshow(image)
fig.update_layout(dragmode="drawrect")

crosshair_kwargs = {
    "showspikes": True,
    "spikemode": "across",
    "spikesnap": "cursor",
    "spikethickness": 0.5,
    "visible": False,
}

fig.update_xaxes(**crosshair_kwargs)
fig.update_yaxes(**crosshair_kwargs)

fig.update_traces(hoverinfo="none", hovertemplate="")

graph_config = {
    "displaylogo": False,
    "displayModeBar": True,
    "scrollZoom": True,
    "modeBarButtons": [["eraseshape", "autoScale2d"]],
}


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(figure=fig, config=graph_config, style={"height": "100%"}),
    ],
    style={"height": "98vh"},
)

if __name__ == "__main__":
    print(f"Annotation tool is running on http://localhost:{os.environ['PORT_FRONTEND']}/")
    app.run_server(host="0.0.0.0", debug=True)
