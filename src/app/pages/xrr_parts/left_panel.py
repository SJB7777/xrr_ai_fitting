from dash import html, dcc, dash_table
from app.logic.materials import INITIAL_LAYERS, MATERIAL_DB

def render_sidebar():
    return html.Div([
        
        # 1. Data Upload (기존 동일)
        html.Div([
            html.Div("1. Data Source", className="sidebar-title"),
            dcc.Upload(
                id='upload-data',
                children=html.Div(['📂 Drag & Drop Data File']),
                style={
                    'width': '100%', 'height': '50px', 'lineHeight': '50px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'borderColor': '#cbd5e1', 'backgroundColor': '#f8fafc',
                    'fontSize': '0.9rem', 'color': '#64748b', 'cursor': 'pointer'
                }
            ),
            html.Div(id='upload-status', style={'fontSize': '0.8rem', 'color': '#64748b', 'marginTop': '5px'})
        ], className="sidebar-section"),

        # 2. Material Library (기존 동일)
        html.Div([
            html.Div("2. Materials (Click to Add)", className="sidebar-title"),
            html.Div([
                html.Div(mat["formula"], className="material-chip", id=f"mat-{mat['formula'].replace('₂','2').replace('₅','5')}")
                for mat in MATERIAL_DB
            ], className="material-grid")
        ], className="sidebar-section"),

        # 3. Layer Definition (수정됨)
        html.Div([
            html.Div("3. Structure Model", className="sidebar-title"),
            
            dash_table.DataTable(
                id='layers-table',
                columns=[
                    {'name': 'Mat', 'id': 'layer', 'editable': True},
                    {'name': 'd(nm)', 'id': 'thickness', 'type': 'numeric', 'editable': True},
                    {'name': 'ρ', 'id': 'density', 'type': 'numeric', 'editable': True},
                    {'name': 'σ', 'id': 'roughness', 'type': 'numeric', 'editable': True},
                ],
                data=INITIAL_LAYERS,
                row_deletable=True,
                
                style_as_list_view=True,
                style_table={'fontSize': '0.8rem'},
                style_header={'backgroundColor': '#f1f5f9', 'fontWeight': 'bold', 'padding': '5px'},
                
                # [중요] 기본 셀 스타일 (선택되지 않았을 때)
                style_cell={
                    'padding': '5px', 
                    'textAlign': 'left',
                    'border': '1px solid #f1f5f9', # 테두리를 옅게 줘서 점프 현상 완화
                    'height': '30px' # 높이 고정
                },
                
                # 조건부 스타일은 이제 Callback에서 동적으로 제어합니다.
                style_data_conditional=[] 
            ),

            # 컨트롤 버튼
            html.Div([
                html.Button("＋ Add", id="btn-add-row", className="btn-secondary", style={'flex': 2}),
                html.Button("▲", id="btn-move-up", className="btn-secondary", style={'flex': 1, 'marginLeft': '5px'}),
                html.Button("▼", id="btn-move-down", className="btn-secondary", style={'flex': 1, 'marginLeft': '5px'}),
            ], style={'display': 'flex', 'marginTop': '10px', 'width': '100%'})

        ], className="sidebar-section"),

        # 4. Fitting Controls (기존 동일)
        html.Div([
            html.Div("4. Fitting Engine", className="sidebar-title"),
            html.Button("🤖 Initialize AI Guess", id="btn-init-ai", className="btn-secondary"),
            html.Button("▶ Start Fitting", id="btn-start-fit", className="btn-primary", style={'marginTop': '10px'}),
            
            html.Div([
                html.Div("Status: Ready", style={'fontWeight': 'bold', 'fontSize': '0.85rem'}),
                html.Div("χ²: 0.0000", style={'color': '#64748b', 'fontSize': '0.8rem'})
            ], style={'marginTop': '15px', 'background': '#f8fafc', 'padding': '10px', 'borderRadius': '5px'})
        ], className="sidebar-section", style={'borderBottom': 'none'}),

    ], className="sidebar")