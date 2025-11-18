import dash
from dash import html, dcc

dash.register_page(__name__, path="/")

layout = html.Div(
    [
        # 메인 컨테이너
        html.Div(
            [
                html.H1("XRR Automated Fitting", style={"textAlign": "center"}),
                html.P(
                    "Upload your XRR dataset and automatically estimate thin-film structure.",
                    style={"textAlign": "center", "fontSize": "18px", "marginTop": "10px"},
                ),
                
                # 샘플 데이터 다운로드 버튼
                html.Div(
                    html.A(
                        "Download Sample Data",
                        href="/assets/sample_data.txt",
                        className="btn-main",
                        style={"display": "inline-block", "marginTop": "20px"}
                    ),
                    style={"textAlign": "center"}
                ),

                # 시작 버튼
                html.Div(
                    dcc.Link(
                        "Start →",
                        href="/app",
                        className="btn-next",
                        style={"display": "inline-block", "marginTop": "20px"}
                    ),
                    style={"textAlign": "center"}
                ),

                # 간단한 안내 텍스트
                html.Div(
                    [
                        html.H3("How to use", style={"marginTop": "40px"}),
                        html.Ul(
                            [
                                html.Li("Upload your XRR dataset in CSV or TXT format."),
                                html.Li("Adjust initial parameters or use auto-generated guesses."),
                                html.Li("Run the fitting algorithm and visualize results."),
                                html.Li("Download the fitted structure and SLD profile."),
                            ],
                            style={"fontSize": "16px"}
                        ),
                    ],
                    style={"maxWidth": "600px", "margin": "40px auto"}
                ),
            ],
            className="section",
            style={"maxWidth": "900px", "margin": "50px auto", "padding": "30px"}
        )
    ],
    className="main-container",
)
