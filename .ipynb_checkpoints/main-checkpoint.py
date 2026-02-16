import pandas as pd
from generate_schedule import generate_schedule
from sim_season import simulate_season
from random_fpi import make_random_fpi
from playoffs import playoff_field
from collections import Counter
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def main():

    df = pd.read_csv("FPI-1-11-26.csv")
    total_tb_counts = Counter()
    for seed in range(2002, 2026):
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

        field, tiebreakers = playoff_field(standings_df, results_df)

        season_tb_counts = Counter(tiebreakers)
        total_tb_counts.update(season_tb_counts)   # or: total_tb_counts += season_tb_counts

        
        print("\nPLAYOFF FIELD (Division winners + Wildcards):")
        print(field)

    print(total_tb_counts)
    print(results_df)
if __name__ == "__main__":
    main()

