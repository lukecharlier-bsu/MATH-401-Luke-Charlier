import numpy as np

def make_random_fpi(df, mean=0.003, std=5.1, seed=1):
    rng = np.random.default_rng(seed)
    df_rand = df.copy()

    df_rand["FPI"] = rng.normal(loc=mean, scale=std, size=len(df_rand))
    df_rand["FPI"] = round(df_rand["FPI"], 1)

    return df_rand
