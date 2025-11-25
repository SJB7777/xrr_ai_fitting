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
    if not layers:
        return np.zeros_like(q)
    for layer in layers:
        if layer["layer"] == "Film":
            params = [ParamSet(layer["thickness"], layer["roughness"], layer["sld"])]
        elif layer["layer"] == "SiO₂":
            sio2_param = ParamSet(layer["thickness"], layer["roughness"], layer["sld"])
    return param2refl(q, params, sio2_param)

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
                    "sld": f"{(d*2.5+0.1):.2f}",
                    "roughness": f"{r:.1f}"
                })
            except:
                table_data.append(layer)
    return table_data