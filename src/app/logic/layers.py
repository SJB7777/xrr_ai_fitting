def insert_new_layer(layers, new_layer):
    new = layers.copy()
    new.insert(len(new) - 1, new_layer)
    return new

def create_layer_from_user_input(formula, t, d, r):
    return {
        "layer": formula,
        "thickness": str(t or "10"),
        "density": str(d or "2.0"),
        "roughness": str(r or "0.3"),
    }
