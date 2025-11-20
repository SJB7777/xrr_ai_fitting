import dash
from dash import html, dcc

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("XRR Automated Fitting", style={"fontSize": "3rem", "marginBottom": "20px", "color": "#1e293b"}),
                html.P(
                    "AI-powered X-Ray Reflectivity Analysis Tool",
                    style={"fontSize": "1.2rem", "color": "#64748b", "marginBottom": "40px"}
                ),
                
                html.Div([
                    dcc.Link(
                        "Start Analysis →",
                        href="/xrr_app",
                        className="btn-primary",
                        style={"textDecoration": "none", "fontSize": "1.1rem", "padding": "15px 30px"}
                    ),
                    html.A(
                        "Download Sample Data",
                        href="/assets/sample_data.txt",
                        className="btn-secondary",
                        style={"textDecoration": "none", "marginLeft": "15px", "padding": "15px 30px"}
                    )
                ], style={"display": "flex", "justifyContent": "center", "alignItems": "center"}),

                # Feature List
                html.Div([
                    html.Div([
                        html.H3("📁 Easy Upload"),
                        html.P("Drag & drop support for .txt, .dat, .xy formats.")
                    ], className="section", style={"padding": "20px", "flex": "1"}),
                    
                    html.Div([
                        html.H3("🤖 AI Prediction"),
                        html.P("Deep Learning model estimates initial parameters.")
                    ], className="section", style={"padding": "20px", "flex": "1"}),
                    
                    html.Div([
                        html.H3("📊 3D Visualization"),
                        html.P("Interactive 3D film stack viewer.")
                    ], className="section", style={"padding": "20px", "flex": "1"}),
                ], style={"display": "flex", "gap": "20px", "marginTop": "60px", "textAlign": "left"})
                
            ],
            style={"maxWidth": "1000px", "margin": "0 auto", "textAlign": "center", "paddingTop": "80px"}
        )
    ],
    className="home-container",
    style={"height": "100vh", "backgroundColor": "#f8fafc"}
)