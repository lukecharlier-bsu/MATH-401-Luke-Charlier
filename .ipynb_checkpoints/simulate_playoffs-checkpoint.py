# simulate_playoffs.py

import pandas as pd
import numpy as np
from sim_game import simulate_game

def reseed(teams_df, mode="four"):
    """
    # Input Variables: teams_df (dataframe), mode (string: "four" or "two")
    # Output Variables: seed_dict (dict) or None
    # Purpose: Sorts a set of playoff teams by Seed and returns a dictionary mapping. Used for playoff matchups (ie, top seeds plays bottom seed)
    # Example: reseed(teams_df, mode="four")
    """
    # sort teams and map them to a dictionary, easier to create this function
    teams_df = teams_df.sort_values("Seed")

    if mode == "four":

        seed_dict = {1: teams_df.iloc[0]["Team"],
                     2: teams_df.iloc[1]["Team"],
                     3: teams_df.iloc[2]["Team"],
                     4: teams_df.iloc[3]["Team"],}

    elif mode == "two":

        seed_dict = {1: teams_df.iloc[0]["Team"],
                     2: teams_df.iloc[1]["Team"],}

    else:
        print("mode must be 'four' or 'two'")
        return None

    return seed_dict

def simulate_round(df, field_df, mode, prev_winners=None, sigma=9, home_field=2, seed=1):
    """
    # Input Variables: df (dataframe of team + FPI), field_df (dataframe of playoff field), mode (string: "wildcard", "divisional",   
    # Input Variables (cont): "conference"), prev_winners (dataframe or None, output from a previous run of this function), sigma (float), 
    # Input Variables (cont): home_field (float), seed (int)
    # Output Variables: round_results_df (dataframe), winners_df (dataframe)
    # Purpose: Simulates a single non super bowl playoff round for both conferences and returns game results plus the winning teams.
    # Example: simulate_round(df, field_df, mode="wildcard", prev_winners=None, sigma=9, home_field=2, seed=1)
    """
    rng = np.random.default_rng(seed) #setting the rng for our simulated games
    power = dict(zip(df["Team"], df["FPI"])) # extract the FPIs from all the teams

    results = []
    winners = []

    for conf, grp in field_df.groupby("Conference"): #loop through each conference individually

        # basically we have a set "mode" so we can group the teams correctly. ie, no 1 seed for wildcard
        if mode == "wildcard":
            seed_dict = dict(zip(grp["Seed"], grp["Team"]))
            games = [(seed_dict[2], seed_dict[7]),(seed_dict[3], seed_dict[6]),(seed_dict[4], seed_dict[5]),] # 2 v 7, 3 v 6, etc

        elif mode == "divisional":
            if prev_winners is None:
                print("You need to load in the previous winners")
                return None

            one_seed = grp.loc[grp["Seed"] == 1, ["Team", "Seed"]] # bring back the 1 seed
            other_seeds = prev_winners.loc[prev_winners["Conference"] == conf, ["Team", "Seed"]] # winners from round 1

            # combine the one seed with the others
            teams = pd.concat([one_seed, other_seeds], ignore_index=True)

            # have every team seeded correctly
            seed_dict = reseed(teams, mode = "four")
            
            games = [(seed_dict[1], seed_dict[4]), (seed_dict[2], seed_dict[3]),]

        elif mode == "conference":
            if prev_winners is None:
                print("You need to load in the previous winners")
                return None

            other_seeds = prev_winners.loc[prev_winners["Conference"] == conf, ["Team", "Seed"]]
            seed_dict = reseed(other_seeds, mode = "two")

            games = [(seed_dict[1], seed_dict[2])]

        else:
            print("You need to put mode as division, conference or wildcard")
            return None

        # simulate games for this conference + round
        for home, away in games:
            margin, home_wins = simulate_game(power1=power[home],power2=power[away],sigma=sigma,home_field=home_field,rng=rng)#simulate all games

            if home_wins:
                winner, loser = home, away
            else:
                winner, loser = away, home

            winners.append({"Team": winner, "Conference": conf}) #save who won
            # create a results section
            results.append({"Round": mode, "Conference": conf, "Home": home, "Away": away, "Winner": winner, "Loser": loser, "Margin": margin})

    round_results_df = pd.DataFrame(results)

    # attach the original seeds to the winners
    winners_df = pd.DataFrame(winners).merge(field_df[["Team", "Seed"]], on="Team", how="left")

    return round_results_df, winners_df

def simulate_playoffs(df, field_df, sigma=9, home_field=2, seed=1):
    """
    # Input Variables: df (dataframe), field_df (dataframe), sigma (float), home_field (float), seed (int)
    # Output Variables: all_playoff_results_df (dataframe), sb_winner (string)
    # Purpose: Simulates the full NFL playoff bracket and returns the results and super bowl winner
    # Example: simulate_playoffs(df, field_df, sigma=9, home_field=2, seed=1)
    """

    # round 1: wild card
    wc_results, wc_winners = simulate_round(df=df, field_df=field_df, mode="wildcard", prev_winners=None,
        sigma=sigma,home_field=home_field,seed=seed)

    # round 2: divisional
    div_results, div_winners = simulate_round(df=df,field_df=field_df,mode="divisional",prev_winners=wc_winners,
        sigma=sigma,home_field=home_field,seed=seed)

    # round 3: conference championship
    conf_results, conf_winners = simulate_round(df=df,field_df=field_df,mode="conference",prev_winners=div_winners,
        sigma=sigma,home_field=home_field,seed=seed)

    # get our winners
    afc_champ = conf_winners.loc[conf_winners["Conference"] == "AFC", "Team"].iloc[0]
    nfc_champ = conf_winners.loc[conf_winners["Conference"] == "NFC", "Team"].iloc[0]

    # SUPER BOWL!!!!!!
    rng = np.random.default_rng(seed) # set the random seed
    power = dict(zip(df["Team"], df["FPI"])) #extract the FPIs

    sb_margin, sb_home_wins = simulate_game(power1=power[afc_champ],power2=power[nfc_champ],sigma=sigma,home_field=0,rng=rng) #play the SB

    if sb_home_wins:
        sb_winner, sb_loser = afc_champ, nfc_champ
    else:
        sb_winner, sb_loser = nfc_champ, afc_champ

    sb_results = pd.DataFrame([{"Round": "super_bowl", "Conference": "Super Bowl", "Home": afc_champ, "Away": nfc_champ,
        "Winner": sb_winner,"Loser": sb_loser,"Margin": sb_margin}])

    # Combine everything
    all_playoff_results_df = pd.concat([wc_results, div_results, conf_results, sb_results],ignore_index=True)

    return all_playoff_results_df, sb_winner