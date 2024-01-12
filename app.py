import dash
import dash_bootstrap_components as dbc

from utilities import debugger

debugger.initialize_if_needed()

app = dash.Dash(
    __name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY]
)
app.title = "SemiAutomaticAnnotation"

server = app.server
