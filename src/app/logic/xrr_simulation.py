import numpy as np


def simulate_xrr(layers):
    q = np.logspace(-2, 1, 500)
    I = q**(-4) * np.exp(-0.1 * q)
    sim = I * 0.95
    return q, I, sim
