from reflecto.exp05_1layer_mask.inference import XRRInferenceEngine


def run_ai_prediction(q_values, intensity_values, wavelength):
    """
    [사용자 정의 함수]
    외부에 있는 AI 예측 코드를 여기에 연결합니다.
    
    Args:
        q_values (list or np.array): q값 배열
        intensity_values (list or np.array): Reflectivity(Intensity) 배열
        wavelength (float): 빔 파장 (Angstrom)
        
    Returns:
        list of dict: Dash DataTable에 들어갈 구조 리스트
    """
    
    print(f"🤖 AI Prediction Start... (WL: {wavelength}Å)")

    weight_path = "resource/weights"
    inference_engine = XRRInferenceEngine(exp_dir=weight_path)
    pred_d, pred_sig, pred_sld = inference_engine.predict(q_values, intensity_values)

    predicted_layers = [
        {"layer": "Si Substrate", "thickness": "∞", "sld": 2.33, "roughness": 0.2},
        {"layer": "SiO₂", "thickness": 10.0, "sld": 2.0, "roughness": 0.4},
        {"layer": "Film", "thickness": float(pred_d), "sld": float(pred_sig), "roughness": float(pred_sld)}
    ]
    # ------------------------------------------

    return predicted_layers