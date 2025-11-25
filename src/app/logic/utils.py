import base64
import io
import pandas as pd
import numpy as np

from reflecto.simulate.simul_genx import param2refl, ParamSet

def parse_contents(contents, filename):
    """업로드된 파일을 파싱하여 Dict 형태로 반환"""
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

def reset_suggestion_table(layers):
    """레이어 구조는 복사하되 값은 ?로 초기화"""
    if not layers: 
        return []
    return [{
        "layer": item.get("layer", "-"),
        "thickness": "?",
        "sld": "?",
        "roughness": "?"
    } for item in layers]

def calculate_xrr_curve(q, layers):
    """물리 엔진을 이용한 시뮬레이션 (0~1 Normalized)"""
    if not layers or q is None or len(q) == 0:
        return np.zeros_like(q) if q is not None else []

    params = []
    sio2_param = None
    
    for layer in layers:
        try:
            t = float(layer.get("thickness", 0)) if str(layer.get("thickness")) not in ["∞", "?"] else 0
            r = float(layer.get("roughness", 0)) if str(layer.get("roughness")) != "?" else 0
            s = float(layer.get("sld", 0)) if str(layer.get("sld")) != "?" else 0
            
            name = layer.get("layer", "")
            
            if "Film" in name:
                params.append(ParamSet(t, r, s))
            elif "SiO" in name: # SiO2, SiO
                sio2_param = ParamSet(t, r, s)
        except (ValueError, TypeError):
            continue

    # 필수 파라미터가 없으면 0 반환
    if not params or sio2_param is None:
        return np.zeros_like(q)

    try:
        intensity = param2refl(q, params, sio2_param)
        return np.abs(intensity) + 1e-10
    except Exception as e:
        print(f"Simulation Error: {e}")
        return np.zeros_like(q)

def format_table_data(layers_data):
    """테이블 표시용 데이터 포맷팅"""
    table_data = []
    if layers_data:
        for layer in layers_data:
            try:
                t = float(layer.get('thickness', 0)) if str(layer.get('thickness')) not in ["∞", "?"] else 0
                d = float(layer.get('sld', 0)) if str(layer.get('sld')) != "?" else 0
                r = float(layer.get('roughness', 0)) if str(layer.get('roughness')) != "?" else 0
                table_data.append({
                    "layer": layer.get("layer", "-"),
                    "thickness": f"{t:.1f}",
                    "sld": f"{d:.2f}", # SLD는 그대로 표시
                    "roughness": f"{r:.1f}"
                })
            except:
                table_data.append(layer)
    return table_data