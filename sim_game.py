import numpy as np

def simulate_game(power1: float, power2: float, sigma: float, home_field: float, rng):
    """
    # Input Variables: power1 (float, home team rating), power2 (float, away team rating), sigma (float), home_field (float), rng (random generator)
    # Output Variables: margin (float), win1 (boolean)
    # Purpose: Simulates the outcome of a single NFL game using team power ratings and randomness
    # Example: simulate_game(10.5, 8.2, 9, 2, rng)
    """
    margin = (power1 - power2) + home_field + (sigma * rng.normal(0, 1))
    win1 = margin > 0
    return margin, win1