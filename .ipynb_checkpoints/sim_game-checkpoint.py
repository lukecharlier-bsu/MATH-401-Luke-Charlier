import numpy as np

def simulate_game(power1: float, power2: float, sigma: float, home_field: float, rng):
    margin = (power1 - power2) + home_field + (sigma * rng.normal(0, 1))  # sigma2 = home advantage constant
    win1 = margin > 0
    return margin, win1

#Example
#simulate_game(50,49,9,2,rng = np.random.default_rng(1))