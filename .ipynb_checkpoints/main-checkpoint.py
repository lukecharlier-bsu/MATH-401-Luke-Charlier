import pandas as pd
from generate_schedule import generate_schedule
from sim_season import simulate_season
from random_fpi import make_random_fpi
from playoffs import playoff_field
from collections import Counter
from real_nfl_schedule import build_real_season_dfs
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

def main():

    df = pd.read_csv("FPI-1-11-26.csv")
    total_tb_counts = Counter()
    total_fpi_counts = Counter()
    for seed in range(2002, 2026):
        #print("\n" + "------------------------------------------------------")
        #print(f"SEASON SIMULATION (seed = {seed})")
        #print("------------------------------------------------------")
    
        df_seeded = make_random_fpi(df,mean=-0.016,std=2.5,seed=seed)
    
        schedule_df = generate_schedule(df_seeded, seed=seed)
        results_df, standings_df = simulate_season(df_seeded,schedule_df,seed=seed)
    
        #print("\nSTANDINGS:")
        #print(standings_df)

        field, tiebreakers, fpi_winners = playoff_field(standings_df, results_df)
        #print(field)
        season_tb_counts = Counter(tiebreakers)
        season_fpi_counts = Counter(fpi_winners)
        total_fpi_counts.update(season_fpi_counts)
        total_tb_counts.update(season_tb_counts)   # or: total_tb_counts += season_tb_counts
    print(total_tb_counts)
    print(total_fpi_counts)
    total_real = Counter()
    
        # Loop through the years and count the # of tiebreakers
    for year in range(2002, 2026):
        results_df, standings_df = build_real_season_dfs(year)
        field, tbs, fpi_winners = playoff_field(standings_df, results_df)
        total_real.update(tbs)
        #print(year, "Playoff field")
        #print(field)
        #print(standings_df)
        
    print(total_real)
    #print(standings_df)
    
    #print(results_df)
if __name__ == "__main__":
    main()

