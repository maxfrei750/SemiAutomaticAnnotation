from dash import dcc, html

# TODO: Type annotations.
# TODO: Documentation.


def get_layout():
    layout = html.Center(
        html.Div(
            [
                html.Br(),
                html.Br(),
                html.H1(dcc.Link("Annotation", href="/apps/annotation")),
                html.H1(dcc.Link("Evaluation", href="/apps/evaluation")),
            ]
        )
    )

    return layout
