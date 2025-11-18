from dash import html, dcc
from .app import app
import dash

app.layout = html.Div(
    [
        # 네비게이션 바
        html.Nav(
            [
                dcc.Link("Home", href="/", className="nav-link"),
                dcc.Link("XRR", href="/xrr_app", className="nav-link"),
            ],
            className="navbar"
        ),

        # 페이지 컨테이너
        dash.page_container
    ],
    style={"fontFamily": "Segoe UI, Tahoma, Geneva, Verdana, sans-serif"}
)

def run() -> None:
    app.run(debug=True, host="0.0.0.0", port=8050)
