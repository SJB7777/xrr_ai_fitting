import numpy as np
from scipy.optimize import least_squares
from reflecto.simulate.simul_genx import param2refl, ParamSet


def run_fitting_algorithm(current_layers, q_exp, I_exp, wavelength):
    """
    [Fitting Engine]
    현재 레이어 파라미터를 초기값으로 하여 최적화를 수행합니다.
    """
    print("🚀 Starting Fitting Process...")

    # 1. 파라미터 추출 (Dict -> Flat Array)
    # 최적화 대상: 각 층의 두께(t), 밀도(d), 거칠기(r)
    # 단, 기판(Substrate)의 두께는 무한대이므로 제외합니다.
    p0 = []
    bounds_min = []
    bounds_max = []
    
    # 파라미터가 어느 레이어의 어떤 속성인지 추적하기 위한 매핑
    param_map = [] 

    for i, layer in enumerate(current_layers):
        # (1) Thickness (기판 제외)
        if layer["thickness"] != "∞":
            val = float(layer.get("thickness", 10))
            p0.append(val)
            param_map.append((i, "thickness"))
            bounds_min.append(0.0)    # 두께 최소값
            bounds_max.append(5000.0) # 두께 최대값

        # (2) sld
        val_d = float(layer.get("sld", 2.33))
        p0.append(val_d)
        param_map.append((i, "sld"))
        bounds_min.append(0.0)
        bounds_max.append(30.0) # 밀도 최대값

        # (3) Roughness
        val_r = float(layer.get("roughness", 0.3))
        p0.append(val_r)
        param_map.append((i, "roughness"))
        bounds_min.append(0.0)
        bounds_max.append(50.0)

    # 2. Cost Function 정의
    def residuals(p):
        # (A) 파라미터 복원 (Array -> Layers)
        temp_layers = [L.copy() for L in current_layers]
        for idx, val in enumerate(p):
            layer_idx, key = param_map[idx]
            temp_layers[layer_idx][key] = val

        # (B) 시뮬레이션 계산 (사용자분의 피팅 함수 연결)
        # ====================================================
        # 👇 [사용자 정의 영역] 가지고 계신 시뮬레이션 함수를 여기에 넣으세요!
        # I_sim = my_custom_xrr_simulation(temp_layers, q_exp, wavelength)
        # ====================================================
        
        # [임시] 데모용 약식 시뮬레이션 (교체 필요)
        # (실제 코드가 없으면 에러가 나므로 임시 로직을 넣었습니다)
        I_sim = calculate_xrr_simulation(q_exp, temp_layers)
        
        # (C) 잔차 계산 (Log scale 차이)
        # 0이나 음수 방지를 위해 log10 적용 전 abs 및 epsilon 추가
        diff = np.log10(np.abs(I_exp) + 1e-10) - np.log10(np.abs(I_sim) + 1e-10)
        return diff

    # 3. 최적화 실행 (Levenberg-Marquardt or TRF)
    res = least_squares(residuals, p0, bounds=(bounds_min, bounds_max), method='trf', ftol=1e-3)

    # 4. 결과 적용 (Flat Array -> Dict List)
    fitted_layers = [L.copy() for L in current_layers]
    for idx, val in enumerate(res.x):
        layer_idx, key = param_map[idx]
        # 소수점 포맷팅
        fitted_layers[layer_idx][key] = f"{val:.2f}"

    print("✅ Fitting Complete!")
    return fitted_layers


def calculate_xrr_simulation(q, layers):

    for layer in layers:
        if layer["layer"] == "Film":
            params = [ParamSet(layer["thickness"], layer["roughness"], layer["sld"])]
        elif layer["layer"] == "SiO₂":
            sio2_param = ParamSet(layer["thickness"], layer["roughness"], layer["sld"])
    return param2refl(q, params, sio2_param)
