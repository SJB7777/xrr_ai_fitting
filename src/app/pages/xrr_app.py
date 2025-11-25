import dash
from dash import html, dcc
from app.callbacks import callbacks 
from app.pages.xrr_parts.left_panel import render_sidebar
from app.pages.xrr_parts.center_panel import render_center_panel
from app.pages.xrr_parts.right_panel import render_right_panel

dash.register_page(__name__, path="/xrr_app")

layout = html.Div([
    dcc.Store(id='xrr-data-store', storage_type='session'),
    dcc.Store(id='ai-param-store', storage_type='memory'),
    dcc.Store(id='fit-status-store', data=False, storage_type='memory'),
    html.Div([
        render_sidebar(),       # 1. 왼쪽 (입력)
        render_center_panel(),  # 2. 중앙 (그래프)
        render_right_panel()    # 3. 오른쪽 (3D + 결과)
    ], className="app-container")
])