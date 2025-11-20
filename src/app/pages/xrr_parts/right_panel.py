from dash import html, dcc, dash_table
from app.components.film_3d import generate_film_stack_figure
from app.logic.materials import INITIAL_LAYERS
import plotly.graph_objects as go

def render_main_content():
    return html.Div([
        
        # === Row 1: Reflectivity & Residual (기존 유지) ===
        html.Div([
            # 1. Main Graph
            html.Div([
                html.H3([html.Span("📈"), " Reflectivity Data"]),
                html.Div([
                    dcc.Graph(
                        id="reflectivity-graph",
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': True, 'responsive': True}
                    )
                ], style={'flex': 1, 'position': 'relative', 'width': '100%', 'height': '100%'})
            ], className="card-box flex-lg"),

            # 2. Residual Graph
            html.Div([
                html.H3([html.Span("📉"), " Error Residual"]),
                html.Div([
                    dcc.Graph(
                        id="residual-graph",
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': False, 'responsive': True}
                    )
                ], style={'flex': 1, 'position': 'relative', 'width': '100%', 'height': '100%'})
            ], className="card-box flex-sm"),
            
        ], className="top-row"),


        # === Row 2: Fourier + Structure + Parameters ===
        html.Div([
            
            # 3. FFT Analysis
            html.Div([
                html.H3([html.Span("🌊"), " FFT Analysis"]),
                html.Div([
                    dcc.Graph(
                        id="fourier-graph",
                        style={'height': '100%', 'width': '100%'},
                        config={'displayModeBar': False, 'responsive': True}
                    )
                ], style={'flex': 1, 'position': 'relative', 'width': '100%', 'height': '100%'})
            ], className="card-box flex-1"),

            # 4. 3D Structure Preview (버튼 복구됨)
            html.Div([
                html.Div([
                    html.Span([html.Span("🧊"), " Structure"], style={'fontWeight': 'bold', 'fontSize': '0.95rem'}),
                    html.Div([
                        # [수정] 누락되었던 Top 버튼 복구 완료
                        html.Button("Top", id="btn-view-top", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px'}),
                        html.Button("Iso", id="btn-view-iso", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px', 'marginLeft': '2px'}),
                        html.Button("Side", id="btn-view-side", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px', 'marginLeft': '2px'}),
                    ])
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '10px 15px', 'backgroundColor': '#f8fafc', 'borderBottom': '1px solid #e2e8f0'}),
                
                html.Div([
                    dcc.Graph(
                        id="film-3d-image",
                        figure=generate_film_stack_figure(INITIAL_LAYERS),
                        style={'width': '100%', 'height': '100%'},
                        config={'displayModeBar': False, 'responsive': True}
                    )
                ], style={'flex': 1, 'position': 'relative', 'width': '100%', 'height': '100%'})
            ], className="card-box flex-1"),

            # 5. Fitted Parameters Table
            html.Div([
                html.H3([html.Span("📋"), " Parameters"]),
                
                html.Div([
                    html.Div([
                        dash_table.DataTable(
                            id='final-params-table',
                            columns=[
                                {'name': 'Mat', 'id': 'layer'},
                                {'name': 'd(Å)', 'id': 'thickness'},
                                {'name': 'SLD', 'id': 'sld'},
                                {'name': 'σ(Å)', 'id': 'roughness'},
                            ],
                            data=[], 
                            style_cell={
                                'textAlign': 'center', 'padding': '4px', 
                                'fontFamily': 'Inter, sans-serif', 'fontSize': '0.8rem',
                                'borderBottom': '1px solid #f1f5f9', 'color': '#334155'
                            },
                            style_header={
                                'backgroundColor': '#ffffff', 'fontWeight': '700', 
                                'borderBottom': '2px solid #e2e8f0', 'color': '#0f172a', 'fontSize': '0.75rem'
                            },
                            style_as_list_view=True
                        )
                    ], style={'flex': '1', 'overflowY': 'auto', 'marginBottom': '5px'}), 

                    html.Button("💾 Export", id="btn-export", className="btn-primary", style={'padding': '6px', 'fontSize': '0.85rem'})
                ], style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'})

            ], className="card-box flex-1"),

        ], className="bottom-row")

    ], className="main-content")