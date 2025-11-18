import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import base64
from io import BytesIO


def generate_film_stack_image(layers_data, view_angle="iso"):
    """
    layers_data: Dash DataTable의 data format
    [
        {"layer": "SiO₂", "thickness": "10.0", ...},
        {"layer": "Cr", "thickness": "5.0", ...},
    ]
    """
    fig = plt.figure(figsize=(8, 10), facecolor='#0a0f1c')
    ax = fig.add_subplot(111, projection='3d')

    # 배경 투명화
    ax.set_facecolor('#0a0f1c')
    ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
    ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

    # 색상 매핑
    colors = {
        "Si": "#4a4a4a", "SiO₂": "#ff9f1c", "Al₂O₃": "#2ec4b6",
        "Cr": "#4cc9f0", "Au": "#ffd23f", "Ti": "#9b5de5",
        "Ta₂O₅": "#f15bb5", "default": "#6c757d"
    }

    z_offset = 0
    for i, layer in enumerate(layers_data):
        name = layer["layer"].split()[0]
        thickness_str = layer["thickness"]

        # 두께 처리
        if thickness_str == "∞":
            thickness = 20  # 기준
        else:
            thickness = float(thickness_str)

        # 3D 바 생성
        ax.bar3d(-2.5, -2.5, z_offset, 5, 5, thickness,
                color=colors.get(name, colors["default"]),
                alpha=0.85, edgecolor='white', linewidth=0.8)

        # 레이블
        if thickness > 2:
            ax.text(0, 0, z_offset + thickness/2,
                    f'{name}\n{thickness_str} nm',
                    color='white', fontsize=9, ha='center', va='center',
                    fontweight='bold',
                    path_effects=[path_effects.withStroke(linewidth=1.5, foreground="black")])  # ✅ 수정
        
        z_offset += thickness

    # 축 설정
    ax.set_zlim(0, max(z_offset, 60))
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_axis_off()

    # 시점
    if view_angle == "top":
        ax.view_init(elev=90, azim=0)
    elif view_angle == "side":
        ax.view_init(elev=0, azim=-90)
    else:
        ax.view_init(elev=25, azim=-135)

    # 이미지 변환
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.2,
                facecolor='#0a0f1c', dpi=120)
    plt.close(fig)
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{encoded}"