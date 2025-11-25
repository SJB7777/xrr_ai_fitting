from dash import html, dcc

def render_center_panel():
    return html.Div([
        
        # 1. Main Reflectivity Graph (가장 크게)
        html.Div([
            html.H3([html.Span("📈"), " Reflectivity Data"]),
            html.Div([
                dcc.Graph(
                    id="reflectivity-graph",
                    style={'height': '100%', 'width': '100%'},
                    config={'displayModeBar': True, 'responsive': True}
                )
            ], style={'flex': 1, 'position': 'relative', 'height': '100%'})
        ], className="card-box", style={'flex': '4', 'minHeight': '350px', 'display': 'flex', 'flexDirection': 'column'}),

        # 2. Residual Graph (중간 위치, 가로 꽉 차게)
        html.Div([
            html.H3([html.Span("📉"), " Residual"]),
            html.Div([
                dcc.Graph(
                    id="residual-graph",
                    style={'height': '100%', 'width': '100%'},
                    config={'displayModeBar': False, 'responsive': True}
                )
            ], style={'flex': 1, 'position': 'relative', 'height': '100%'})
        ], className="card-box", style={'flex': '2', 'minHeight': '200px', 'display': 'flex', 'flexDirection': 'column'}),

        # 3. FFT Graph (맨 아래 위치, 가로 꽉 차게)
        html.Div([
            html.H3([html.Span("🌊"), " FFT Analysis"]),
            html.Div([
                dcc.Graph(
                    id="fourier-graph",
                    style={'height': '100%', 'width': '100%'},
                    config={'displayModeBar': False, 'responsive': True}
                )
            ], style={'flex': 1, 'position': 'relative', 'height': '100%'})
        ], className="card-box", style={'flex': '2', 'minHeight': '200px', 'display': 'flex', 'flexDirection': 'column'}),

    ], className="center-panel")