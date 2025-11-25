MATERIALS = ["Si", "SiO2", "Al2O3", "Cr", "Au", "Ti", "Ta2O5"]

# Initial sample data
INITIAL_LAYERS = [
    {"layer": "Si Substrate", "thickness": "∞", "sld": "2.33", "roughness": "0.2"},
    {"layer": "SiO₂", "thickness": "10.0", "sld": "2.20", "roughness": "0.3"},
    {"layer": "Cr", "thickness": "5.0", "sld": "7.19", "roughness": "0.5"},
]

# Material database
MATERIAL_DB = [
    {"formula": "Si", "name": "Silicon", "sld": "2.33"},
    {"formula": "SiO₂", "name": "Silicon Dioxide", "sld": "2.20"},
    {"formula": "Al₂O₃", "name": "Aluminum Oxide", "sld": "3.95"},
    {"formula": "Cr", "name": "Chromium", "sld": "7.19"},
    {"formula": "Au", "name": "Gold", "sld": "19.32"},
    {"formula": "Ti", "name": "Titanium", "sld": "4.51"},
    {"formula": "Ta₂O₅", "name": "Tantalum Pentoxide", "sld": "8.20"},
]
