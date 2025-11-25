import plotly.graph_objects as go
import numpy as np

def create_comparison_graph(q, i_exp, i_ai, i_fit):
    """
    3가지 라인을 그리는 메인 그래프
    1. Exp (Blue Dots)
    2. AI Prediction (Yellow/Orange Dashed)
    3. Final Fit (Red Solid)
    """
    fig = go.Figure()
    
    # 1. Experimental Data (항상 표시)
    if i_exp is not None:
        fig.add_trace(go.Scatter(
            x=q, y=i_exp, mode='markers', name='Experimental', 
            marker=dict(size=4, color='#2563eb', symbol='circle-open', opacity=0.6)
        ))
    
    # 2. AI Prediction (AI값이 있을 때만)
    if i_ai is not None:
        fig.add_trace(go.Scatter(
            x=q, y=i_ai, mode='lines', name='AI Prediction', 
            line=dict(color='#f59e0b', width=2, dash='dash') # Amber color
        ))
        
    # 3. Final Fit (피팅값이 있을 때만)
    if i_fit is not None:
        fig.add_trace(go.Scatter(
            x=q, y=i_fit, mode='lines', name='Final Fit', 
            line=dict(color='#dc2626', width=3) # Red solid
        ))

    # 레이아웃 설정 (데이터가 없으면 빈 화면 유지)
    if q is not None:
        fig.update_layout(
            template="plotly_white", margin=dict(l=60, r=20, t=20, b=50),
            xaxis=dict(title="q (Å⁻¹)", type="linear", showgrid=True, gridcolor='#e2e8f0'),
            yaxis=dict(title="Reflectivity", type="log", showgrid=True, gridcolor='#e2e8f0'),
            legend=dict(x=0.98, y=0.98, xanchor='right', yanchor='top', bgcolor='rgba(255,255,255,0.8)')
        )
    else:
        fig.update_layout(template="plotly_white", xaxis={'visible': False}, yaxis={'visible': False})
        
    return fig

def create_residual_graph(q, i_exp, i_target, label="Resid"):
    """Residual Graph 생성"""
    min_len = min(len(i_exp), len(i_target))
    # 로그 차이 계산
    diff = np.log10(i_exp[:min_len]) - np.log10(i_target[:min_len])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=q[:min_len], y=diff, mode='lines', name=label,
        line=dict(color='#64748b', width=1), 
        fill='tozeroy', fillcolor='rgba(100, 116, 139, 0.2)'
    ))
    fig.update_layout(
        template="plotly_white", margin=dict(l=50, r=20, t=20, b=50),
        xaxis=dict(title="q (Å⁻¹)", showgrid=True, gridcolor='#e2e8f0'),
        yaxis=dict(title="Δ log R", showgrid=True, gridcolor='#e2e8f0'),
        showlegend=False,
        shapes=[dict(type="line", x0=q[0], x1=q[-1], y0=0, y1=0, line=dict(color="#0f172a", width=1, dash="dash"))]
    )
    return fig

def create_fft_graph(q, i_exp):
    """FFT Graph 생성"""
    r_norm = i_exp * (q ** 4)
    r_norm = r_norm - np.mean(r_norm)
    n = len(q)
    d_q = q[1] - q[0] if n > 1 else 0.01
    fft_amp = np.abs(np.fft.rfft(r_norm))
    z_space = np.fft.rfftfreq(n, d=d_q) * 2 * np.pi 
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=z_space, y=fft_amp, mode='lines', name='FFT',
        line=dict(color='#059669', width=2),
        fill='tozeroy', fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    fig.update_layout(
        template="plotly_white", margin=dict(l=50, r=20, t=20, b=50),
        xaxis=dict(title="Thickness (Å)", showgrid=True, gridcolor='#e2e8f0', range=[0, 300]),
        yaxis=dict(title="Amplitude", showgrid=True, gridcolor='#e2e8f0', showticklabels=False),
        showlegend=False
    )
    return fig