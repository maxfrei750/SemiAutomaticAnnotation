from typing import List, Union

import dash_bootstrap_components as dbc
from dash.development.base_component import Component


class Message(dbc.Col):
    def __init__(self, children: Union[Component, List[Component]], color: str = "info"):
        super().__init__(
            dbc.Alert(children, color=color),
            style={"margin-top": "10%"},
            width={"size": 6, "offset": 3},
        )
