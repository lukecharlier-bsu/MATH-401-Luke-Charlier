import numpy as np

def simulate_game(power1: float, power2: float, sigma: float, home_field: float, rng):
    """
    # Input Variables: power1 (float, home team rating), power2 (float, away team rating), sigma (float), home_field (float), rng (random generator)
    # Output Variables: margin (float), win1 (boolean)
    # Purpose: Simulates the outcome of a single NFL game using team power ratings and randomness
    # Example: simulate_game(10.5, 8.2, 9, 2, rng)
    """
    margin = (power1 - power2) + home_field + (sigma * rng.normal(0, 1))  # sigma2 = home advantage constant
    win1 = margin > 0
    return margin, win1

#Example
#simulate_game(50,49,9,2,rng = np.random.default_rng(1))

#Inspo for total games
#https://perthirtysix.com/nfl/scorigami
#https://jamescurley.blog/posts/2021-10-03-nfl-scorelines/