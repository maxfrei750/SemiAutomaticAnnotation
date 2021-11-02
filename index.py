import os

from dash import dcc, html
from dash.dependencies import Input, Output

from app import app
from apps import annotation, evaluation, menu

PORT_FRONTEND = int(os.environ["PORT_FRONTEND"])

app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/apps/annotation":
        return annotation.get_layout()
    elif pathname == "/apps/evaluation":
        return evaluation.get_layout()
    else:
        return menu.get_layout()


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=PORT_FRONTEND, debug=True, dev_tools_ui=False)
