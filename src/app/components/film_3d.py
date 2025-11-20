import plotly.graph_objects as go

def generate_film_stack_figure(layers_data, view_angle="iso"):
    """
    Plotly Mesh3d를 사용하여 박막 적층 구조를 3D로 시각화합니다.
    """
    fig = go.Figure()
    
    if not layers_data:
        return fig

    # 색상 매핑
    colors = {
        "Si": "#4a4a4a", "SiO₂": "#ff9f1c", "Al₂O₃": "#2ec4b6",
        "Cr": "#4cc9f0", "Au": "#ffd23f", "Ti": "#9b5de5",
        "Ta₂O₅": "#f15bb5", "default": "#6c757d"
    }

    z_current = 0
    
    # 바닥부터 쌓기 위해 역순 처리 혹은 인덱스 조정 (여기선 순서대로 쌓음)
    for layer in reversed(layers_data):
        name = layer["layer"].split()[0]
        try:
            thickness = float(layer["thickness"]) if layer["thickness"] != "∞" else 20.0
        except (ValueError, TypeError):
            thickness = 10.0

        color = colors.get(name, colors["default"])
        
        # 육면체 생성 (x, y: -5~5)
        x = [-5, -5, 5, 5, -5, -5, 5, 5]
        y = [-5, 5, 5, -5, -5, 5, 5, -5]
        z = [z_current, z_current, z_current, z_current, 
             z_current + thickness, z_current + thickness, z_current + thickness, z_current + thickness]
        
        # Mesh3d의 i, j, k 인덱스 (육면체의 12개 삼각형 면)
        fig.add_trace(go.Mesh3d(
            x=x, y=y, z=z,
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color=color,
            opacity=0.9,
            name=f"{name} ({thickness}nm)",
            flatshading=True,
            showscale=False
        ))
        
        z_current += thickness

    # 카메라 시점 설정
    camera = dict(eye=dict(x=1.5, y=1.5, z=1.5))
    if view_angle == "top":
        camera = dict(eye=dict(x=0, y=0, z=2.5), up=dict(x=0, y=1, z=0))
    elif view_angle == "side":
        camera = dict(eye=dict(x=2.5, y=0, z=0))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(title="Thickness (nm)", range=[0, max(60, z_current)]),
            camera=camera,
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    return fig