import numpy as np

def make_random_fpi(df, mean=-0.016, std=2.5, seed=1):
    """
    # Input Variables: df (dataframe of NFL teams), mean (float), std (float), seed (int)
    # Output Variables: df_rand (dataframe) — copy of df with randomized FPI ratings
    # Purpose: Generates synthetic FPI ratings for all 32 teams drawn from a normal distribution
    # Example: make_random_fpi(df, mean=-0.016, std=3, seed=42)
    """
    rng = np.random.default_rng(seed)
    df_rand = df.copy()

    df_rand["FPI"] = rng.normal(loc=mean, scale=std, size=len(df_rand))
    df_rand["FPI"] = round(df_rand["FPI"], 1)

    return df_rand
