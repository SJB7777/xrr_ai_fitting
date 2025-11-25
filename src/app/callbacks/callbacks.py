import pandas as pd
import numpy as np
from dash import callback, Output, Input, State, ctx, no_update
import plotly.graph_objects as go

from app.components.film_3d import generate_film_stack_figure
from app.logic.materials import INITIAL_LAYERS, MATERIAL_DB
from app.logic.ai_interface import run_ai_prediction
from app.logic.fitting import run_fitting_algorithm

from app.logic.utils import parse_contents, reset_suggestion_table, calculate_xrr_curve, format_table_data
from app.logic.plotting import create_comparison_graph, create_residual_graph, create_fft_graph

# 1. 파일 업로드
@callback(
    Output('xrr-data-store', 'data'),
    Output('upload-status', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_output(contents, filename):
    if contents:
        data = parse_contents(contents, filename)
        return (data, f"✅ Loaded: {filename}") if data else (None, "❌ Error")
    return None, "Awaiting upload..."

# 2. 테이블 하이라이트
@callback(
    Output("layers-table", "style_data_conditional"),
    Input("layers-table", "active_cell")
)
def highlight_active_row(active_cell):
    style = [{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}]
    if active_cell:
        style.append({
            'if': {'row_index': active_cell['row']},
            'backgroundColor': '#e0f2fe',
            'border': '1px solid #3b82f6',
            'fontWeight': 'bold'
        })
    return style

# 3. Layers Table & Status Update
@callback(
    [Output("layers-table", "data", allow_duplicate=True),
     Output("layers-table", "active_cell"),
     Output("ai-results-table", "data"),
     Output("ai-param-store", "data"),
     Output("fit-status-store", "data")], 
    
    [Input(f"mat-{mat['formula'].replace('₂','2').replace('₅','5')}", "n_clicks") for mat in MATERIAL_DB],
    Input("btn-init-ai", "n_clicks"),
    Input("btn-apply-ai", "n_clicks"),
    Input("btn-add-row", "n_clicks"),
    Input("btn-move-up", "n_clicks"),
    Input("btn-move-down", "n_clicks"),
    Input("btn-start-fit", "n_clicks"),
    
    State("layers-table", "data"),
    State("layers-table", "active_cell"),
    State("ai-results-table", "data"),
    State("xrr-data-store", "data"),
    State("input-wavelength", "value"),
    prevent_initial_call=True
)
def update_layers_table(*args):
    if not ctx.triggered: return [no_update]*5
    triggered_id = ctx.triggered_id
    
    layers_data = list(args[-5]) if args[-5] else []
    active_cell = args[-4]
    ai_data_stored = args[-3]
    xrr_store_data = args[-2]
    wavelength_val = args[-1]
    wl = float(wavelength_val or 1.54)
    
    new_layer = None
    structure_changed = False 
    
    # 1. 재료 추가
    if triggered_id.startswith("mat-"):
        formula = triggered_id.replace("mat-", "")
        defaults = {"Si": 2.33, "SiO2": 2.20, "Al2O3": 3.95, "Cr": 7.19, "Au": 19.32}
        new_layer = {"layer": formula, "thickness": 10.0, "sld": defaults.get(formula.replace('2','₂').replace('5','₅'), 2.0), "roughness": 0.3}
    
    # 2. AI 초기화
    elif triggered_id == "btn-init-ai":
        if not xrr_store_data: return [no_update]*5
        df = pd.DataFrame(xrr_store_data)
        ai_prediction = run_ai_prediction(df['q'].values, df['intensity'].values, wl)
        return no_update, no_update, ai_prediction, ai_prediction, False

    # 3. Fitting 수행
    elif triggered_id == "btn-start-fit":
        if not xrr_store_data or not layers_data: return [no_update]*5
        df = pd.DataFrame(xrr_store_data)
        fitted_layers = run_fitting_algorithm(layers_data, df['q'].values, df['intensity'].values, wl)
        return no_update, no_update, fitted_layers, no_update, True

    # 4. 제안 적용
    elif triggered_id == "btn-apply-ai":
        if ai_data_stored:
            return ai_data_stored, None, no_update, no_update, False
        return [no_update]*5

    # 5. 행 조작
    elif triggered_id == "btn-add-row":
        new_layer = {"layer": "New Layer", "thickness": 10.0, "sld": 2.0, "roughness": 0.3}
    elif triggered_id in ["btn-move-up", "btn-move-down"]:
        move = -1 if "up" in triggered_id else 1
        if active_cell:
            idx = active_cell['row']
            target = idx + move
            if 0 <= target < len(layers_data):
                layers_data[idx], layers_data[target] = layers_data[target], layers_data[idx]
                active_cell['row'] = target
                structure_changed = True
                return layers_data, active_cell, reset_suggestion_table(layers_data), no_update, False

    if new_layer:
        layers_data.append(new_layer)
        structure_changed = True
        
    if structure_changed:
        return layers_data, no_update, reset_suggestion_table(layers_data), no_update, False
        
    return [no_update]*5

# 4. 3D View Update
@callback(
    Output("film-3d-image", "figure"),
    Input("layers-table", "data"),
    Input("btn-view-top", "n_clicks"),
    Input("btn-view-side", "n_clicks"),
    Input("btn-view-iso", "n_clicks"),
    prevent_initial_call=False
)
def update_3d_view(layers_data, *args):
    view = "iso"
    if ctx.triggered_id == "btn-view-top": view = "top"
    elif ctx.triggered_id == "btn-view-side": view = "side"
    return generate_film_stack_figure(layers_data or INITIAL_LAYERS, view)

# 5. 통합 그래프 업데이트 (스케일링 적용)
@callback(
    [Output("reflectivity-graph", "figure"),
     Output("residual-graph", "figure"),
     Output("fourier-graph", "figure"),
     Output("final-params-table", "data")],
    [Input("layers-table", "data"),       
     Input("xrr-data-store", "data"),
     Input("input-wavelength", "value"),
     Input("ai-param-store", "data"),
     Input("ai-results-table", "data"),
     Input("fit-status-store", "data")]
)
def update_graphs_and_results(layers_manual, uploaded_data, wavelength, ai_params, right_panel_data, is_fitted):
    
    # 1. Exp Data Prep & Scaling Factor 계산
    if not uploaded_data:
        # 데이터가 없을 때: Mock 데이터로 스케일 1.0 설정
        q_exp = np.linspace(0.01, 0.5, 500)
        scale_factor = 1.0 
        
        # 빈 그래프 리턴 (깔끔하게)
        empty_fig = go.Figure()
        empty_fig.update_layout(template="plotly_white", xaxis={'visible':False}, yaxis={'visible':False})
        return empty_fig, empty_fig, empty_fig, []
    else:
        df = pd.DataFrame(uploaded_data)
        q_exp = df['q'].values
        # 원본 Intensity
        raw_intensity = df['intensity'].values
        # Log용 0 처리
        i_exp = np.where(raw_intensity <= 0, 1e-10, raw_intensity)
        
        # 🔥 [중요] 스케일 팩터 = 실험 데이터의 최대값
        scale_factor = np.max(i_exp) if len(i_exp) > 0 else 1.0

    # 2. Curve Calculation (Normalize -> Multiply by Scale Factor)
    
    # (A) AI Curve
    i_ai = None
    if ai_params:
         # 0~1로 정규화된 시뮬레이션 * 실험데이터 최대값
         i_ai = calculate_xrr_curve(q_exp, ai_params) * scale_factor

    # (B) Fit Curve
    i_fit = None
    if is_fitted and right_panel_data:
        valid = not any(str(r.get('thickness')) == '?' for r in right_panel_data)
        if valid:
            i_fit = calculate_xrr_curve(q_exp, right_panel_data) * scale_factor

    # (C) Manual Curve (Residual Fallback용)
    i_man = calculate_xrr_curve(q_exp, layers_manual) * scale_factor

    # 3. Graph Generation
    fig_main = create_comparison_graph(q_exp, i_exp, i_ai, i_fit)
    
    target_sim = i_fit if i_fit is not None else (i_ai if i_ai is not None else i_man)
    label_resid = "Resid (Fit)" if i_fit is not None else ("Resid (AI)" if i_ai is not None else "Resid (Manual)")
    
    fig_resid = create_residual_graph(q_exp, i_exp, target_sim, label_resid)
    fig_fft = create_fft_graph(q_exp, i_exp)
    
    table_data = format_table_data(layers_manual)

    return fig_main, fig_resid, fig_fft, table_data