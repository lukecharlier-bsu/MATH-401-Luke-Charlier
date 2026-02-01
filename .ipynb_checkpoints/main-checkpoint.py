import pandas as pd
from generate_schedule import generate_schedule
from sim_season import simulate_season
from random_fpi import make_random_fpi
from playoffs import playoff_field
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def main():

    df = pd.read_csv("FPI-1-11-26.csv")
    
    for seed in range(1, 10):
        print("\n" + "------------------------------------------------------")
        print(f"SEASON SIMULATION (seed = {seed})")
        print("------------------------------------------------------")
    
        df_seeded = make_random_fpi(
            df,
            mean=-0.016,
            std=2.5,
            seed=seed
        )
    
        schedule_df = generate_schedule(df_seeded, seed=seed)
        results_df, standings_df = simulate_season(
            df_seeded,
            schedule_df,
            seed=seed
        )
    
        print("\nSTANDINGS:")
        print(standings_df)
    
        field = playoff_field(standings_df, results_df)
    
        print("\nPLAYOFF FIELD (Division winners + Wildcards):")
        print(field)

    
if __name__ == "__main__":
    main()

