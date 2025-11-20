import dash
from dash import html, dcc
from app.callbacks import callbacks 
from app.pages.xrr_parts.left_panel import render_sidebar
from app.pages.xrr_parts.right_panel import render_main_content

dash.register_page(__name__, path="/xrr_app")

layout = html.Div([
    # [중요] 데이터를 브라우저에 저장할 공간 생성 (화면엔 안보임)
    dcc.Store(id='xrr-data-store', storage_type='memory'), 
    
    html.Div([
        render_sidebar(),      
        render_main_content()  
    ], className="app-container")
])