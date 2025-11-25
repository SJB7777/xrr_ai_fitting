from reflecto_backend.api import ai_guess
import numpy as np

def run_ai_prediction(tths: np.ndarray, refl: np.ndarray, wavelen: float):
    """
    [사용자 정의 함수]
    외부에 있는 AI 예측 코드를 여기에 연결합니다.
    
    Args:
        tths (list or np.array): q값 배열
        refl (list or np.array): Reflectivity(Intensity) 배열
        wavelength (float): 빔 파장 (Angstrom)
        
    Returns:
        list of dict: Dash DataTable에 들어갈 구조 리스트
    """
    
    print(f"🤖 AI Prediction Start... (WL: {wavelen}Å)")

    film_params, sio2_param = ai_guess(tths, refl, wavelen)

    predicted_layers = [
        {"layer": "Si Substrate", "thickness": "∞", "sld": 2.33, "roughness": 0.2},
        {"layer": "SiO₂", "thickness": sio2_param.thickness, "sld": sio2_param.sld, "roughness": sio2_param.roughness},
    ]
    for param in film_params:
        predicted_layers.append(
            {"layer": "Film",
            "thickness": param.thickness,
            "sld": param.sld,
            "roughness": param.roughness}
        )

    return predicted_layers