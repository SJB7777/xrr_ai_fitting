import base64
import io
import pandas as pd
from dash import callback, Output, Input, State, ctx, no_update
import plotly.graph_objects as go
import numpy as np
from app.components.film_3d import generate_film_stack_figure
from app.logic.materials import INITIAL_LAYERS, MATERIAL_DB

# === 1. 데이터 파싱 헬퍼 ===
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')), 
            sep=None, engine='python', header=None, names=['q', 'intensity']
        )
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        return df.to_dict('records')
    except Exception as e:
        print(f"Error parsing file: {e}")
        return None

# === Callbacks ===

# 2. 파일 업로드
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


@callback(
    Output("layers-table", "style_data_conditional"),
    Input("layers-table", "active_cell")
)
def highlight_active_row(active_cell):
    # 기본 스타일 (홀수 행 배경색 등)
    style = [
        {'if': {'row_index': 'odd'}, 'backgroundColor': '#f9fafb'}
    ]
    
    # 선택된 행이 있다면 진하게 하이라이트
    if active_cell:
        style.append({
            'if': {'row_index': active_cell['row']},
            'backgroundColor': '#e0f2fe',  # 연한 파란색 배경
            'border': '1px solid #3b82f6', # 파란색 테두리
            'fontWeight': 'bold'
        })
    
    return style


# 3. Layers Table Update (위치 이동 로직 수정: selected_rows -> active_cell)
@callback(
    [Output("layers-table", "data", allow_duplicate=True),
     Output("layers-table", "active_cell")],  # [추가] 하이라이트 위치를 제어하기 위해 Output 추가
    
    [Input(f"mat-{mat['formula'].replace('₂','2').replace('₅','5')}", "n_clicks") for mat in MATERIAL_DB],
    Input("btn-init-ai", "n_clicks"),
    Input("btn-add-row", "n_clicks"),
    Input("btn-move-up", "n_clicks"),
    Input("btn-move-down", "n_clicks"),
    
    State("layers-table", "data"),
    State("layers-table", "active_cell"),
    prevent_initial_call=True
)
def update_layers_table(*args):
    if not ctx.triggered: return no_update, no_update
    triggered_id = ctx.triggered_id
    
    # args 파싱
    layers_data = list(args[-2]) if args[-2] else []
    active_cell = args[-1]
    
    new_layer = None
    
    # 1. 재료 칩 클릭
    if triggered_id.startswith("mat-"):
        formula = triggered_id.replace("mat-", "")
        defaults = {"Si": 2.33, "SiO2": 2.20, "Al2O3": 3.95, "Cr": 7.19, "Au": 19.32}
        new_layer = {"layer": formula, "thickness": 10.0, "density": defaults.get(formula.replace('2','₂').replace('5','₅'), 2.0), "roughness": 0.3}
    
    # 2. AI 초기화
    elif triggered_id == "btn-init-ai":
        import random
        # 초기화 시 하이라이트 해제(None) 또는 유지(no_update)
        return [
            {"layer": "Si Substrate", "thickness": "∞", "density": 2.33, "roughness": 0.2}, 
            {"layer": "SiO₂", "thickness": 10.0, "density": 2.20, "roughness": 0.3}
        ], None 

    # 3. 빈 행 추가
    elif triggered_id == "btn-add-row":
        new_layer = {"layer": "New Layer", "thickness": 10.0, "density": 2.0, "roughness": 0.3}
        
    # 4. 순서 변경 (위로) ▲ [핵심 수정]
    elif triggered_id == "btn-move-up":
        if not active_cell: return no_update, no_update
        idx = active_cell['row']
        
        if idx > 0:
            # 데이터 Swap
            layers_data[idx], layers_data[idx-1] = layers_data[idx-1], layers_data[idx]
            # [중요] 하이라이트도 위로 한 칸 이동
            active_cell['row'] = idx - 1 
            return layers_data, active_cell
            
    # 5. 순서 변경 (아래로) ▼ [핵심 수정]
    elif triggered_id == "btn-move-down":
        if not active_cell: return no_update, no_update
        idx = active_cell['row']
        
        if idx < len(layers_data) - 1:
            # 데이터 Swap
            layers_data[idx], layers_data[idx+1] = layers_data[idx+1], layers_data[idx]
            # [중요] 하이라이트도 아래로 한 칸 이동
            active_cell['row'] = idx + 1
            return layers_data, active_cell

    # 데이터 추가 로직 (맨 뒤에 추가)
    if new_layer:
        layers_data.append(new_layer)
        # 추가할 때는 하이라이트 변경 없음 (no_update)
        return layers_data, no_update
        
    return no_update, no_update

# 4. 3D View Update (기존 유지 - 에러 방지 추가)
@callback(
    Output("film-3d-image", "figure"),
    Input("layers-table", "data"),
    Input("btn-view-top", "n_clicks"),
    Input("btn-view-side", "n_clicks"),
    Input("btn-view-iso", "n_clicks"),
    prevent_initial_call=False
)
def update_3d_view(layers_data, b1, b2, b3):
    view = "iso"
    if ctx.triggered_id == "btn-view-top": view = "top"
    elif ctx.triggered_id == "btn-view-side": view = "side"
    return generate_film_stack_figure(layers_data or INITIAL_LAYERS, view)

# 5. 통합 그래프 업데이트
@callback(
    [Output("reflectivity-graph", "figure"),
     Output("residual-graph", "figure"),
     Output("fourier-graph", "figure"),     # [추가] FFT 그래프
     Output("final-params-table", "data")],
    [Input("layers-table", "data"),
     Input("xrr-data-store", "data")]
)
def update_graphs_and_results(layers_data, uploaded_data):
    # 1. 데이터 준비 (기존 동일)
    if uploaded_data:
        df = pd.DataFrame(uploaded_data)
        q_exp = df['q'].values
        intensity_exp = df['intensity'].values
        q_sim = q_exp 
    else:
        # 선형 간격의 q 생성 (FFT를 위해 선형이 유리함)
        q_exp = np.linspace(0.01, 0.5, 500) 
        # Mock: 100Å 두께의 진동 패턴 (sin(100*q))
        intensity_exp = q_exp**(-4) * np.exp(-0.02 * q_exp) * (1 + 0.5 * np.sin(100 * q_exp)) + np.random.normal(0, 1e-7, len(q_exp))
        intensity_exp = np.abs(intensity_exp) + 1e-10
        q_sim = q_exp

    # Mock Simulation
    intensity_sim = q_sim**(-4) * np.exp(-0.02 * q_sim) * (1 + 0.45 * np.sin(100 * q_sim + 0.1))
    intensity_sim = np.abs(intensity_sim) + 1e-10

    # --- Graph 1: Main Reflectivity (기존 동일) ---
    fig_main = go.Figure()
    fig_main.add_trace(go.Scatter(x=q_exp, y=intensity_exp, mode='markers', name='Exp', marker=dict(size=3, color='#2563eb', symbol='circle-open')))
    fig_main.add_trace(go.Scatter(x=q_sim, y=intensity_sim, mode='lines', name='Sim', line=dict(color='#dc2626', width=2)))
    fig_main.update_layout(
        template="plotly_white", margin=dict(l=60, r=20, t=20, b=50),
        xaxis=dict(title="q (Å⁻¹)", type="linear", showgrid=True, gridcolor='#e2e8f0'),
        yaxis=dict(title="Reflectivity", type="log", showgrid=True, gridcolor='#e2e8f0'),
        legend=dict(x=0.98, y=0.98, xanchor='right', yanchor='top', bgcolor='rgba(255,255,255,0.8)')
    )

    # --- Graph 2: Residual (기존 동일) ---
    min_len = min(len(intensity_exp), len(intensity_sim))
    diff = np.log10(np.abs(intensity_exp[:min_len]) + 1e-10) - np.log10(np.abs(intensity_sim[:min_len]) + 1e-10)
    
    fig_resid = go.Figure()
    fig_resid.add_trace(go.Scatter(x=q_exp[:min_len], y=diff, mode='lines', name='Resid', line=dict(color='#64748b', width=1), fill='tozeroy', fillcolor='rgba(100, 116, 139, 0.2)'))
    fig_resid.update_layout(
        template="plotly_white", margin=dict(l=50, r=20, t=20, b=50),
        xaxis=dict(title="q (Å⁻¹)", type="linear", showgrid=True, gridcolor='#e2e8f0'),
        yaxis=dict(title="Δ log R", showgrid=True, gridcolor='#e2e8f0'),
        showlegend=False,
        shapes=[dict(type="line", x0=q_exp[0], x1=q_exp[-1], y0=0, y1=0, line=dict(color="#0f172a", width=1, dash="dash"))]
    )

    # --- [New] Graph 3: Fourier Transform (FFT) ---
    # XRR에서 FFT는 보통 R * q^4 (Fresnel 정규화) 값에 대해 수행하여 두께(Thickness) 성분을 찾습니다.
    
    # 1. 데이터 전처리 (RQ^4)
    r_norm = intensity_exp * (q_exp ** 4)
    # 2. DC 성분(평균) 제거 (FFT 0점 피크 방지)
    r_norm = r_norm - np.mean(r_norm)
    
    # 3. FFT 수행
    n = len(q_exp)
    d_q = q_exp[1] - q_exp[0] if n > 1 else 0.01
    fft_amp = np.abs(np.fft.rfft(r_norm))
    fft_freq = np.fft.rfftfreq(n, d=d_q)
    
    # 4. X축 변환: 주파수(1/q) -> 두께 공간(Å) (z = 2π/Δq 대략적 변환)
    # XRR FFT에서 x축은 보통 Thickness(z)에 비례합니다. (2π/q_period)
    z_space = fft_freq * 2 * np.pi 

    fig_fft = go.Figure()
    fig_fft.add_trace(go.Scatter(
        x=z_space, y=fft_amp, mode='lines', name='FFT',
        line=dict(color='#059669', width=2), # Green color
        fill='tozeroy', fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    
    fig_fft.update_layout(
        template="plotly_white", margin=dict(l=50, r=20, t=20, b=50),
        xaxis=dict(title="Thickness (Å)", showgrid=True, gridcolor='#e2e8f0', range=[0, 300]), # 관심 영역 줌인
        yaxis=dict(title="Amplitude", showgrid=True, gridcolor='#e2e8f0', showticklabels=False), # 진폭 크기는 상대적임
        showlegend=False
    )

    # --- 4. Table Data (기존 동일) ---
    table_data = []
    if layers_data:
        for layer in layers_data:
            try:
                thick_raw = layer.get('thickness', 0)
                dens_raw = layer.get('density', 0)
                rough_raw = layer.get('roughness', 0)
                
                thick = float(thick_raw) if thick_raw and str(thick_raw).strip() != '' else 0.0
                dens = float(dens_raw) if dens_raw and str(dens_raw).strip() != '' else 0.0
                rough = float(rough_raw) if rough_raw and str(rough_raw).strip() != '' else 0.0

                sld_val = dens * 2.5 + 0.1
                table_data.append({
                    "layer": layer.get("layer", "-"),
                    "thickness": f"{thick:.1f}",
                    "sld": f"{sld_val:.2f}",
                    "roughness": f"{rough:.1f}"
                })
            except: continue

    return fig_main, fig_resid, fig_fft, table_data