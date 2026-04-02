import pandas as pd
import nflreadpy as nfl
from collections import Counter
from playoffs import playoff_field
from random_fpi import make_random_fpi

def build_real_season_dfs(year: int, tm_cap=100):
    """
    # Input Variables: year (int, NFL season year)
    # Output Variables: results_df (dataframe), standings_df (dataframe)
    # Purpose: Loads real NFL game results for a given season and formats them to match the simulation structure
    # Example: build_real_nfl_schedule(2022)
    """
    # Load in the schedules
    sch = nfl.load_schedules([year]).to_pandas()

    # Keep all regular season games
    sch = sch[(sch["season"] == year) & (sch["game_type"] == "REG")].copy()

    # Load in NFL Team Data, need to convert to pandas cause the nflreadpy is weird
    teams = nfl.load_teams().to_pandas()

    # Connect the NFL Team Data to the abbreviations in the schedule section
    team_cols = ["team_abbr", "team_name", "team_conf", "team_division"]

    # Do a left join for all home teams in the results
    sch = sch.merge(teams[team_cols],left_on="home_team",right_on="team_abbr").rename(columns={ "team_name": "Home",
        "team_conf": "Home_Conf", "team_division": "Home_Div"
        }).drop(columns=["team_abbr"])

    # Do a left join for all the away teams in the results
    sch = sch.merge(teams[team_cols],left_on="away_team",right_on="team_abbr").rename(columns={"team_name": "Away",
        "team_conf": "Away_Conf","team_division": "Away_Div"
        }).drop(columns=["team_abbr"])
  
    # Keep track of the margins for every game
    home_score = sch["home_score"]
    away_score = sch["away_score"]
    margin_home = home_score - away_score
    capped_margin_home = margin_home.clip(lower=-tm_cap, upper=tm_cap)
    
    # Create an empty pandas series to store each game's winner and loser
    winner = pd.Series([None] * len(sch), index=sch.index)
    loser  = pd.Series([None] * len(sch), index=sch.index)
    tie = pd.Series([None] * len(sch), index=sch.index)

    # home wins if margin > 0, away wins if less than 0
    home_win = margin_home > 0
    away_win = margin_home < 0
    both_tie = margin_home == 0

    # Attach winners and losers based on the boolean function into the winner and lsoer series
    winner[home_win] = sch.loc[home_win, "Home"]
    loser[home_win]  = sch.loc[home_win, "Away"]  
    winner[away_win] = sch.loc[away_win, "Away"]
    loser[away_win]  = sch.loc[away_win, "Home"]
    tie_home = sch.loc[both_tie, "Home"]
    tie_away = sch.loc[both_tie, "Away"]
    # Create the results dataframe, exactly in the format I created my results in for the simulations
    results_df = pd.DataFrame({"Home": sch["Home"],"Away": sch["Away"],"Winner": winner,
        "Loser": loser, "Tie": tie, "Divisional": sch["Home_Div"] == sch["Away_Div"],
        "Conference": sch["Home_Conf"] == sch["Away_Conf"], "Margin": margin_home,
        "Home_Score": home_score, "Away_Score": away_score,
    })

    #group teams by amount of wins
    wins = results_df["Winner"].value_counts()
    losses = results_df["Loser"].value_counts()
    ties = pd.concat([tie_home, tie_away], ignore_index=True).value_counts()

  
    # map teams wins and losses to the standings
    standings = pd.DataFrame({"Team": teams["team_name"].unique()})
    standings["Wins"] = standings["Team"].map(wins).fillna(0).astype(int)
    standings["Losses"] = standings["Team"].map(losses).fillna(0).astype(int)
    standings["Ties"] = standings["Team"].map(ties).fillna(0).astype(int)

    div_wins = results_df.loc[results_df["Divisional"], "Winner"].value_counts()
    conf_wins = results_df.loc[results_df["Conference"], "Winner"].value_counts()
    div_losses = results_df.loc[results_df["Divisional"], "Loser"].value_counts()
    conf_losses = results_df.loc[results_df["Conference"], "Loser"].value_counts()    
    div_ties = results_df.loc[results_df["Conference"], "Tie"].value_counts()
    conf_ties = results_df.loc[results_df["Conference"], "Tie"].value_counts()
    # map teams divisional and conference wins
    standings["Div_Wins"] = standings["Team"].map(div_wins).fillna(0).astype(int)
    standings["Conf_Wins"] = standings["Team"].map(conf_wins).fillna(0).astype(int)
    standings["Div_Losses"] = standings["Team"].map(div_losses).fillna(0).astype(int)
    standings["Conf_Losses"] = standings["Team"].map(conf_losses).fillna(0).astype(int)
    standings["Div_Ties"] = standings["Team"].map(div_ties).fillna(0).astype(int)
    standings["Conf_Ties"] = standings["Team"].map(conf_ties).fillna(0).astype(int)

    # map all teams to correct conference and division
    team_info = teams.set_index("team_name")[["team_conf", "team_division"]]
    standings["Conference"] = standings["Team"].map(team_info["team_conf"].to_dict())
    standings["Division"] = standings["Team"].map(team_info["team_division"].to_dict())

    # cummulative margin for home and away teams grouped by team
    home_margin = (results_df["Home_Score"] - results_df["Away_Score"]).groupby(results_df["Home"]).sum()
    away_margin = (results_df["Away_Score"] - results_df["Home_Score"]).groupby(results_df["Away"]).sum()

    # merge them together
    total_margin = home_margin.add(away_margin, fill_value=0)
    standings["Total_Margin"] = standings["Team"].map(total_margin).fillna(0).astype(int)

    capped_home_margin = (results_df["Home_Score"] - results_df["Away_Score"]).clip(lower=-tm_cap, upper=tm_cap)  #ADD
    capped_away_margin = (results_df["Away_Score"] - results_df["Home_Score"]).clip(lower=-tm_cap, upper=tm_cap)  #ADD
    
    home_capped = capped_home_margin.groupby(results_df["Home"]).sum()  #ADD
    away_capped = capped_away_margin.groupby(results_df["Away"]).sum()  #ADD

    capped_total = home_capped.add(away_capped, fill_value=0)  #ADD
    standings["Capped_Margin"] = standings["Team"].map(capped_total).fillna(0).astype(int)
   
    # remove teams with no wins/losses (ie, Oakland Raiders)
    standings = standings[~((standings["Wins"] == 0) & (standings["Losses"] == 0))]
 
    # Sort the standings by wins and total margin
    standings_df = standings.sort_values(["Wins", "Total_Margin"], ascending=[False, False]).reset_index(drop=True)
    standings_df = make_random_fpi(standings_df, seed=year)
    return results_df, standings_df

def real_schedule_df(year:int):
     # Load in the schedules
    sch = nfl.load_schedules([year]).to_pandas()

    # Keep all regular season games
    sch = sch[(sch["season"] == year) & (sch["game_type"] == "REG")].copy()

    # Load in NFL Team Data, need to convert to pandas cause the nflreadpy is weird
    teams = nfl.load_teams().to_pandas()

    # Connect the NFL Team Data to the abbreviations in the schedule section
    team_cols = ["team_abbr", "team_name", "team_conf", "team_division"]

    # Do a left join for all home teams in the results
    sch = sch.merge(teams[team_cols],left_on="home_team",right_on="team_abbr").rename(columns={ "team_name": "Home",
        "team_conf": "Home_Conf", "team_division": "Home_Div"
        }).drop(columns=["team_abbr"])

    # Do a left join for all the away teams in the results
    sch = sch.merge(teams[team_cols],left_on="away_team",right_on="team_abbr").rename(columns={"team_name": "Away",
        "team_conf": "Away_Conf","team_division": "Away_Div"
        }).drop(columns=["team_abbr"])

    # Build schedule_df in your format
    schedule_df = pd.DataFrame({"Home": sch["Home"], "Away": sch["Away"],
        "Divisional": sch["Home_Div"] == sch["Away_Div"], "Conference": sch["Home_Conf"] == sch["Away_Conf"],})

    return schedule_df.reset_index(drop=True)

