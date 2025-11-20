def generate_ai_initial_guess():
    import random
    return [
      {"layer":"Si Substrate", "thickness":"∞","density":"2.33","roughness":"0.2"},
      {"layer":"SiO₂", "thickness":f"{random.uniform(8,12):.1f}",
       "density":"2.20","roughness":f"{random.uniform(0.2,0.4):.1f}"},
    ]
