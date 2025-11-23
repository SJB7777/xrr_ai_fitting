from dash import html, dcc, dash_table
from app.components.film_3d import generate_film_stack_figure
from app.logic.materials import INITIAL_LAYERS

def render_right_panel():
    return html.Div([
        
        # 1. 3D Structure Viewer (상단)
        html.Div([
            html.Div([
                html.Span([html.Span("🧊"), " 3D Model"], style={'fontWeight': 'bold'}),
                html.Div([
                    html.Button("Top", id="btn-view-top", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px'}),
                    html.Button("Iso", id="btn-view-iso", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px', 'marginLeft': '2px'}),
                    html.Button("Side", id="btn-view-side", className="btn-secondary", style={'fontSize':'0.7rem', 'padding':'2px 6px', 'marginLeft': '2px'}),
                ])
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '10px 15px', 'borderBottom': '1px solid #e2e8f0', 'background': '#f8fafc'}),
            
            html.Div([
                dcc.Graph(
                    id="film-3d-image",
                    figure=generate_film_stack_figure(INITIAL_LAYERS),
                    style={'width': '100%', 'height': '100%'},
                    config={'displayModeBar': False}
                )
            ], style={'flex': 1, 'minHeight': '300px'})
            
        ], className="card-box", style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),


        # 2. Results & Comparison (하단 - 탭 이름 변경)
        html.Div([
            html.H3([html.Span("📊"), " Results"]), # 타이틀 변경 (Parameters -> Results)
            
            dcc.Tabs([
                # [수정] Tab 1: Final Fit (최종 결과)
                dcc.Tab(
                    label='🎯 Final Fit', 
                    children=[
                        html.Div([
                            dash_table.DataTable(
                                id='final-params-table',
                                columns=[
                                    {'name': 'Mat', 'id': 'layer'},
                                    {'name': 'd(Å)', 'id': 'thickness'},
                                    {'name': 'ρ', 'id': 'density'},
                                    {'name': 'σ', 'id': 'roughness'},
                                ],
                                data=[], 
                                style_cell={'textAlign': 'center', 'padding': '4px', 'fontSize': '0.8rem'},
                                style_header={'backgroundColor': '#fff', 'fontWeight': 'bold', 'borderBottom': '2px solid #e2e8f0'},
                                style_as_list_view=True
                            ),
                            html.Button("💾 Export CSV", id="btn-export", className="btn-primary", style={'marginTop': 'auto', 'padding': '8px'})
                        ], style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'})
                    ], 
                    style={'borderBottom': '1px solid #e2e8f0'}, 
                    selected_style={'borderBottom': '3px solid #2563eb', 'color': '#2563eb', 'fontWeight': 'bold'}
                ),

                # [수정] Tab 2: AI Guess (AI 제안)
                dcc.Tab(
                    label='🤖 AI Guess', 
                    children=[
                        html.Div([
                            html.Div("AI Predicted Structure:", style={'fontSize':'0.8rem', 'color':'#64748b', 'marginBottom':'5px'}),
                            
                            dash_table.DataTable(
                                id='ai-results-table',
                                columns=[
                                    {'name': 'Mat', 'id': 'layer'},
                                    {'name': 'd(Å)', 'id': 'thickness'},
                                    {'name': 'ρ', 'id': 'density'},
                                    {'name': 'σ', 'id': 'roughness'},
                                ],
                                data=[],
                                style_cell={'textAlign': 'center', 'padding': '4px', 'fontSize': '0.8rem', 'color': '#64748b'},
                                style_header={'backgroundColor': '#f0fdf4', 'fontWeight': 'bold', 'color': '#166534'},
                                style_as_list_view=True
                            ),
                            html.Button("✅ Apply AI", id="btn-apply-ai", className="btn-primary", 
                                        style={'marginTop': 'auto', 'backgroundColor': '#16a34a', 'padding': '8px'})
                        ], style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'})
                    ], 
                    style={'borderBottom': '1px solid #e2e8f0'}, 
                    selected_style={'borderBottom': '3px solid #16a34a', 'color': '#16a34a', 'fontWeight': 'bold'}
                )

            ], style={'height': '40px'}, content_style={'flex': 1, 'display': 'flex', 'flexDirection': 'column'})

        ], className="card-box", style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'minHeight': '300px'})

    ], className="right-panel")