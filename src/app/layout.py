from dash import html, dcc
import dash
from .app import app

app.layout = html.Div(
    [
        # === Top Navigation Bar ===
        html.Header(
            [
                # 1. 좌측: 로고 및 앱 이름
                html.Div(
                    dcc.Link(
                        [
                            html.Span("XRR", style={"color": "#2563eb"}), # 파란색 강조
                            html.Span("Fit", style={"color": "#0f172a"}),
                            html.Span("AI", style={"color": "#64748b", "fontWeight": "400", "marginLeft": "5px", "fontSize": "1rem"})
                        ],
                        href="/", 
                        className="navbar-brand"
                    ),
                    className="navbar-left"
                ),

                # 2. 우측: 메뉴 링크들
                html.Nav(
                    [
                        dcc.Link(
                            [html.Span("🏠"), " Home"], 
                            href="/", 
                            className="nav-link"
                        ),
                        dcc.Link(
                            [html.Span("📊"), " Analysis"], 
                            href="/xrr_app", 
                            className="nav-link"
                        ),
                        # 기능이 없어도 있어보이게 넣는 더미 링크 (추후 구현)
                        html.A(
                            [html.Span("📘"), " Docs"], 
                            href="#", 
                            className="nav-link",
                            style={"cursor": "not-allowed", "opacity": "0.6"}
                        ),
                        html.A(
                            [html.Span("⚙️"), " Settings"], 
                            href="#", 
                            className="nav-link",
                            style={"cursor": "not-allowed", "opacity": "0.6"}
                        ),
                    ],
                    className="navbar-right"
                )
            ],
            className="navbar"
        ),

        # === Page Content ===
        dash.page_container
    ],
    style={"fontFamily": "Inter, Segoe UI, sans-serif", "height": "100vh", "display": "flex", "flexDirection": "column"}
)