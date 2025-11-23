from dash import html, dcc

def render_center_panel():
    return html.Div([
        
        # 1. Main Reflectivity Graph (크게)
        html.Div([
            html.H3([html.Span("📈"), " Reflectivity Data"]),
            html.Div([
                dcc.Graph(
                    id="reflectivity-graph",
                    style={'height': '100%', 'width': '100%'},
                    config={'displayModeBar': True, 'responsive': True}
                )
            ], style={'flex': 1, 'position': 'relative', 'height': '100%'})
        ], className="card-box", style={'flex': '3', 'minHeight': '400px'}),

        # 2. Bottom Row (Residual & FFT) - 작게 병렬 배치
        html.Div([
            
            # Residual
            html.Div([
                html.H3([html.Span("📉"), " Residual"]),
                dcc.Graph(id="residual-graph", style={'height': '100%'}, config={'displayModeBar': False})
            ], className="card-box", style={'flex': 1}),

            # FFT
            html.Div([
                html.H3([html.Span("🌊"), " FFT"]),
                dcc.Graph(id="fourier-graph", style={'height': '100%'}, config={'displayModeBar': False})
            ], className="card-box", style={'flex': 1}),

        ], style={'display': 'flex', 'gap': '20px', 'flex': '2', 'minHeight': '250px'})

    ], className="center-panel")