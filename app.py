import dash
import plotly.io as pio

pio.templates.default = "plotly_white"

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
