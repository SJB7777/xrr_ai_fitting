import numpy as np
from scipy.optimize import least_squares
from reflecto.simulate.simul_genx import param2refl, ParamSet

def run_fitting_algorithm(current_layers, q_exp, I_exp, wavelength):
    """
    [Fitting Engine]
    현재 레이어 파라미터를 초기값으로 하여 최적화를 수행합니다.
    """
    print("🚀 Starting Fitting Process...")

    # [수정] 실험 데이터의 스케일 팩터 계산 (Max Value)
    scale_factor = np.max(I_exp) if len(I_exp) > 0 else 1.0

    # 1. 파라미터 추출 (Dict -> Flat Array)
    p0 = []
    bounds_min = []
    bounds_max = []
    param_map = [] 

    for i, layer in enumerate(current_layers):
        # (1) Thickness (기판 제외)
        if layer["thickness"] != "∞":
            val = float(layer.get("thickness", 10))
            p0.append(val)
            param_map.append((i, "thickness"))
            bounds_min.append(0.0)
            bounds_max.append(5000.0)

        # (2) SLD (Density 대신 SLD 사용)
        val_s = float(layer.get("sld", 2.0))
        p0.append(val_s)
        param_map.append((i, "sld"))
        bounds_min.append(0.0)
        bounds_max.append(50.0) 

        # (3) Roughness
        val_r = float(layer.get("roughness", 0.3))
        p0.append(val_r)
        param_map.append((i, "roughness"))
        bounds_min.append(0.0)
        bounds_max.append(50.0)

    # 2. Cost Function 정의
    def residuals(p):
        # (A) 파라미터 복원
        temp_layers = [L.copy() for L in current_layers]
        for idx, val in enumerate(p):
            layer_idx, key = param_map[idx]
            temp_layers[layer_idx][key] = val

        # (B) 시뮬레이션 계산 (Normalized 0~1)
        I_sim_norm = calculate_xrr_simulation(q_exp, temp_layers)
        
        # [수정] 스케일 적용 (Normalized * Scale Factor)
        I_sim_scaled = I_sim_norm * scale_factor
        
        # (C) 잔차 계산 (Log scale)
        diff = np.log10(np.abs(I_exp) + 1e-10) - np.log10(np.abs(I_sim_scaled) + 1e-10)
        return diff

    # 3. 최적화 실행
    try:
        res = least_squares(residuals, p0, bounds=(bounds_min, bounds_max), method='trf', ftol=1e-3)
        
        # 4. 결과 적용
        fitted_layers = [L.copy() for L in current_layers]
        for idx, val in enumerate(res.x):
            layer_idx, key = param_map[idx]
            fitted_layers[layer_idx][key] = float(val) # float 변환

        print("✅ Fitting Complete!")
        return fitted_layers
    except Exception as e:
        print(f"❌ Fitting Failed: {e}")
        return current_layers

def calculate_xrr_simulation(q, layers):
    # utils의 함수와 비슷하지만, fitting 내부에서 빠르게 돌기 위해 재정의하거나 import해서 사용
    # 여기서는 직접 구현
    params = []
    sio2_param = None
    
    for layer in layers:
        try:
            t = float(layer.get("thickness", 0)) if str(layer.get("thickness")) not in ["∞", "?"] else 0
            r = float(layer.get("roughness", 0))
            s = float(layer.get("sld", 0))
            
            name = layer.get("layer", "")
            if "Film" in name:
                params.append(ParamSet(t, r, s))
            elif "SiO" in name:
                sio2_param = ParamSet(t, r, s)
        except: continue

    if not params or sio2_param is None:
        return np.zeros_like(q)
        
    return param2refl(q, params, sio2_param)