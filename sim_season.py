import numpy as np
import pandas as pd
from sim_game import simulate_game


def simulate_season(df, schedule_df, sigma=9, home_field=2, seed=1, tm_cap=10):
    """
    # Name: simulate_season
    # Input Variables: df (dataframe), schedule_df (dataframe), sigma (int), home_field (int), seed (int), tm_cap (int)
    # Output Variables: results_df (dataframe containing the winner and loser of all games), standings_df (dataframe showing NFL standings)
    # Purpose: Simulates an entire 17 game 32 team NFL season
    # Note: tm_cap=10 is the intended default for analysis (caps per-game margin at 10 pts to reduce blowout skew)
    # Example: simulate_season(df_seeded, schedule_df, sigma=9, home_field=2, seed=1, tm_cap=10)
    """
    rng = np.random.default_rng(seed)

    teams = df["Team"].tolist() # All 32 NFL teams
    power = dict(zip(df["Team"], df["FPI"])) # Pairs teams with their assigned rating
    division = dict(zip(df["Team"], df["Division"])) 
    
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

        results.append({"Home": home,"Away": away,"Winner": winner,"Loser": loser, "Divisional": divisional, "Conference": conference, "Margin": margin,})

    results_df = pd.DataFrame(results)
    results_df["Tie"] = results_df["Margin"] == 0
    
    # Count the wins ---------------------------------------
    wins = {}
    div_wins = {}
    conf_wins = {}
    div_losses = {}
    conf_losses = {}
    total_margin = {}
    capped_margin = {}
    games_played = {}
    

    # Start every team out with 0 wins
    for team in teams:
        wins[team] = 0
        div_wins[team] = 0
        conf_wins[team] = 0
        div_losses[team] = 0
        conf_losses[team] = 0
        total_margin[team] = 0
        capped_margin[team] = 0
        games_played[team] = 0
        
    # Count wins from results
    for _, r in results_df.iterrows():
        home = r["Home"]
        away = r["Away"]
        winner = r["Winner"]
        loser = r["Loser"]
        wins[winner] += 1
        games_played[home] += 1
        games_played[away] += 1
    
        if r["Divisional"]:
            div_wins[winner] += 1
            div_losses[loser] += 1
    
        if r["Conference"]:
            conf_wins[winner] += 1
            conf_losses[loser] += 1

        total_margin[home] += r["Margin"] #add margin to home teams total
        total_margin[away] -= r["Margin"] #subtract margin from away teams total
        if r["Margin"] > 0:
            cap = min(r["Margin"], tm_cap)
        else:
            cap = max(r["Margin"], -tm_cap)
        
        capped_margin[home] += cap
        capped_margin[away] -= cap
        #let's say home team loses by 5, then away team's margin will be - -5, which would add 5 to it.
    
    # Standings ---------------------------------------------
    standings = []

    for team in teams:
        standings.append({"Team": team,"Wins": wins[team], "Losses": games_played[team] - wins[team], "FPI": power[team],"Div_Wins": 
                          div_wins[team],"Conf_Wins": conf_wins[team],"Division": division[team], "Total_Margin": total_margin[team], 
                          "Capped_Margin": capped_margin[team], "Div_Losses": div_losses[team],"Conf_Losses": conf_losses[team],
                         })

    standings_df = pd.DataFrame(standings)
    standings_df["Ties"] = 0
    standings_df["Div_Ties"] = 0
    standings_df["Conf_Ties"] = 0
    # Sort standings by wins (descending) -------------------
    standings_df = standings_df.sort_values(by="Wins", ascending=False).reset_index(drop=True)
    
    #Creating the "FPI vs True difference" -------------------
    standings_df["Final_Rank"] = standings_df.index + 1
    fpi_ranks = (df.sort_values("FPI", ascending=False).reset_index(drop=True))
    fpi_ranks["FPI_Rank"] = fpi_ranks.index + 1

    standings_df = standings_df.merge(fpi_ranks[["Team", "FPI_Rank"]],on="Team",how="left")
    standings_df["Conference"] = standings_df["Division"].str.split().str[0]

    standings_df["FPI vs True difference"] = (standings_df["FPI_Rank"] - standings_df["Final_Rank"])
    standings_df.drop(columns=["Final_Rank"], inplace=True)
    return results_df, standings_df