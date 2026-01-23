import pandas as pd
from generate_schedule import generate_schedule
from sim_season import simulate_season
from random_fpi import make_random_fpi
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
def main():
    df = pd.read_csv("FPI-1-11-26.csv")

    df = make_random_fpi(df, mean=-0.016249999999999876, std=2.467759174738909, seed=1)
        
    schedule_df = generate_schedule(df, seed=5)
    #print(schedule_df)
    #print(schedule_df.head())
    results_df, standings_df = simulate_season(df, schedule_df, seed=345)
    print(standings_df)
    print(schedule_df[(schedule_df["Home"] == "Green Bay Packers") | (schedule_df["Away"] == "Green Bay Packers")])
    print(schedule_df[(schedule_df["Home"] == "Detroit Lions") | (schedule_df["Away"] == "Detroit Lions")])
    print(schedule_df[(schedule_df["Home"] == "Chicago Bears") | (schedule_df["Away"] == "Chicago Bears")])
    print(schedule_df[(schedule_df["Home"] == "Minnesota Vikings") | (schedule_df["Away"] == "Minnesota Vikings")])
if __name__ == "__main__":
    main()

