import numpy as np
import pandas as pd
from sim_game import simulate_game

def simulate_season(df, schedule_df, sigma=9, home_field=2, seed=1):
    rng = np.random.default_rng(seed)
    n_games = 17

    teams = df["Team"].tolist() # All 32 NFL teams
    power = dict(zip(df["Team"], df["FPI"])) # Pairs teams with their assigned rating

    # -Simulate all games -----------------------------------
    results = []  # Will store every game's results

    for _, row in schedule_df.iterrows(): # The _, is to ignore the index
        home = row["Home"]
        away = row["Away"]
        divisional = row["Divisional"]
        conference = row["Conference"]
        
        # Simulate the game
        margin, home_wins = simulate_game(power1= power[home], power2= power[away],sigma=sigma,home_field=home_field,rng = rng)

        # Store the result
        if home_wins:
            winner = home
            loser = away
        else:
            winner = away
            loser = home

        results.append({"Home": home,"Away": away,"Winner": winner,"Loser": loser, "Divisional": divisional, "Conference": conference})

    results_df = pd.DataFrame(results)
    
    # Count the wins ---------------------------------------
    wins = {}
    div_wins = {}
    conf_wins = {}


    # Start every team out with 0 wins
    for team in teams:
        wins[team] = 0
        div_wins[team] = 0
        conf_wins[team] = 0
        
    # Count wins from results
    for _, r in results_df.iterrows():
        winner = r["Winner"]
        wins[winner] += 1
    
        if r["Divisional"]:
            div_wins[winner] += 1
    
        if r["Conference"]:
            conf_wins[winner] += 1
    
    # Standings ---------------------------------------------
    standings = []

    for team in teams:
        standings.append({"Team": team,"Wins": wins[team], "Losses": n_games - wins[team], "FPI": power[team],"Div_Wins": div_wins[team],
                         "Conf_Wins": conf_wins[team],})

    standings_df = pd.DataFrame(standings)

    # Sort standings by wins (descending) -------------------
    standings_df = standings_df.sort_values(by="Wins", ascending=False).reset_index(drop=True)
    
    #Creating the "FPI vs True difference" -------------------
    standings_df["Final_Rank"] = standings_df.index + 1
    fpi_ranks = (df.sort_values("FPI", ascending=False).reset_index(drop=True))
    fpi_ranks["FPI_Rank"] = fpi_ranks.index + 1

    standings_df = standings_df.merge(fpi_ranks[["Team", "FPI_Rank"]],on="Team",how="left")

    standings_df["FPI vs True difference"] = (standings_df["FPI_Rank"] - standings_df["Final_Rank"])
    standings_df.drop(columns=["Final_Rank", "FPI_Rank"], inplace=True)
    return results_df, standings_df