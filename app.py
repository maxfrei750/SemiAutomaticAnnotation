import dash
import dash_bootstrap_components as dbc

# TODO: Use bootstrap components to make use of bootstrap theme.

app = dash.Dash(
    __name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY]
)
server = app.server
