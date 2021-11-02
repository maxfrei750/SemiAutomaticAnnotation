from dash import html


def get_layout(message: str):
    layout = html.Div(
        [
            html.Center(
                [
                    html.H1(message),
                ]
            )
        ],
        style={"height": "98vh"},
    )

    return layout
