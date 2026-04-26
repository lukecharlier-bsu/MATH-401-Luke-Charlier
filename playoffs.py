# playoffs.py
import pandas as pd
import numpy as np

def nfl_win_pct(standings_df, t1, mode="normal"):
    """
    Input Variables: standings_df (dataframe), t1 (string, ie Football team), mode (string: normal, conference, division)
    Output Variables: win percentage (float)
    Purpose: Calculates a team’s win percentage under different tiebreaking contexts
    Example: nfl_win_pct(standings_df, "Packers", mode="conference")
    """
    row = standings_df.loc[standings_df["Team"] == t1].iloc[0]

    if mode == "conference":
        wins = row["Conf_Wins"]
        losses = row["Conf_Losses"]
        ties = row.get("Conf_Ties", 0)

    elif mode == "division":
        wins = row["Div_Wins"]
        losses = row["Div_Losses"]
        ties = row.get("Div_Ties", 0)

    else:
        # default = overall record
        wins = row["Wins"]
        losses = row["Losses"]
        ties = row.get("Ties", 0)

    games = wins + losses + ties

    if games == 0:
        return 0

    return (wins + 0.5 * ties) / games

# Name: head_to_head
def head_to_head(results_df,t1,t2):
    """
    Input Variables: results_df (dataframe), t1 (string, ie Football team), t2 (string, ie Football team)
    Output Variables: Will return the team that has the better record OR none if they've never played/have equal record
    Purpose: Looks at 2 teams and sees who has the better record against each other
    Example: head_to_head(results_df,"Green Bay Packers","New Orleans Saints")
    """
    games = results_df[((results_df["Home"] == t1) & (results_df["Away"] == t2)) |((results_df["Home"] == t2) & (results_df["Away"] == t1))].copy()
    # Above makes a copy of every matchup between the 2 teams

    if len(games) == 0: #if they have never play, return
        return None

    t1_wins = (games["Winner"] == t1).sum() #Add up the games where team 1 wins
    t2_wins = (games["Winner"] == t2).sum() #Add up the games where team 2 wins

    if t1_wins > t2_wins:
        return t1
    if t2_wins > t1_wins:
        return t2
    return None

# Name: division_record
def division_record(standings_df,t1,t2):
    """
    Input Variables: standings_df (dataframe), t1 (string, ie Football team), t2 (string, ie Football team)
    Output Variables: team name (string) or None
    Purpose: Breaks ties using divisional wins
    Example: division_record(standings_df, "Packers", "Lions")
    """
    w1 = nfl_win_pct(standings_df,t1,mode = "division")
    w2 = nfl_win_pct(standings_df,t2,mode = "division")
    if w1 > w2:
        return t1
    if w2 > w1:
        return t2
    return None

# Name: conference_record
def conference_record(standings_df,t1,t2):
    """
    Input Variables: standings_df (dataframe), t1 (string), t2 (string)
    Output Variables: team name (string) or None
    Purpose: Breaks ties using conference wins
    Example: conference_record(standings_df, "Eagles", "Cowboys")
    """
    w1 = nfl_win_pct(standings_df,t1,mode = "conference")
    w2 = nfl_win_pct(standings_df,t2,mode = "conference")

    if w1 > w2:
        return t1
    if w2 > w1:
        return t2
    return None

# Name: common_games
def common_games(results_df, t1, t2):
    """
    Input Variables: results_df (dataframe), t1 (string), t2 (string)
    Output Variables: team name (string) or None
    Purpose: Breaks ties using wins against common opponents
    Example: common_games(results_df, "49ers", "Seahawks")
    """
    # Opponents each team played
    # set() function allows us to get a clean intersection
    t1_opponents = set(results_df.loc[results_df["Home"] == t1, "Away"]) | set(results_df.loc[results_df["Away"] == t1, "Home"])
    t2_opponents = set(results_df.loc[results_df["Home"] == t2, "Away"]) | set(results_df.loc[results_df["Away"] == t2, "Home"])

    # Common opponents (remove each other so head to head doesn't sneak in)
    common = (t1_opponents & t2_opponents) - {t1, t2}
    
    # NFL rule: must have at least 4 common opponents
    if len(common) < 4:
        return None
        
    # Take note the # of games played against these opponents for t1
    # This is needed for win percentage, as common opponents can have a diff number for t1 and t2
    t1_games = results_df[((results_df["Home"] == t1) & (results_df["Away"].isin(common))) |
        ((results_df["Away"] == t1) & (results_df["Home"].isin(common)))]
    # Take note the # of games played against these opponents for t2
    t2_games = results_df[((results_df["Home"] == t2) & (results_df["Away"].isin(common))) |
        ((results_df["Away"] == t2) & (results_df["Home"].isin(common)))]
    
    # Count wins vs common opponents using Winner/Loser
    t1_wins = ((results_df["Winner"] == t1) & (results_df["Loser"].isin(common))).sum()
    t2_wins = ((results_df["Winner"] == t2) & (results_df["Loser"].isin(common))).sum()

    # We need to use win percentage 
    t1_pct = t1_wins / len(t1_games)
    t2_pct = t2_wins / len(t2_games)

    if t1_pct > t2_pct:
        return t1
    if t2_pct > t1_pct:
        return t2
    return None

def strength_of_victory(results_df, standings_df, team):
    """
    Input Variables: results_df (dataframe), standings_df (dataframe), team (string)
    Output Variables: mean of wins between teams they beat (integer)
    Purpose: Breaks ties using mean wins of beaten teams
    Example: strength_of_victory(results_df, standings_df, "Green Bay Packers")
    """
    beaten = results_df.loc[results_df["Winner"] == team, "Loser"].tolist() # List of teams the selected team beat

    if len(beaten) == 0:
        return 0

    wins = standings_df.loc[standings_df["Team"].isin(beaten), "Wins"] #stores all the wins of the teams they beat

    return wins.mean() # takes the mean of those teams

def strength_of_schedule(results_df, standings_df, team):
    """
    Input Variables: results_df (dataframe), standings_df (dataframe), team (string)
    Output Variables: mean of wins between opponents (integer)
    Purpose: Breaks ties using mean wins of opponents
    Example: strength_of_schedule(results_df, standings_df, "Green Bay Packers")
    """
    opponents_home = results_df.loc[results_df["Home"] == team, "Away"].tolist()

    opponents_away = results_df.loc[results_df["Away"] == team, "Home"].tolist()

    opponents = opponents_home + opponents_away

    if len(opponents) == 0:
        return 0

    wins = standings_df.loc[standings_df["Team"].isin(opponents), "Wins"] #stores all the wins of the teams they played

    return wins.mean() # takes the mean of those teams

def fpi_result(winner, higher_fpi):
    """
    Input Variables: winner (str), higher_fpi (str or None):
    Output Variables: result (str)
    Purpose: Just allows us to do a quick check if the "higher FPI" team won a tiebreaker
    Example: fpi_result("Jets", "Bills") -> "lower FPI won"
    """
    if higher_fpi is None:
        return "FPI tied"
    if winner == higher_fpi:
        return "higher FPI won"
    return "lower FPI won"

def tie_break(results_df, standings_df, t1, t2, mode="division"):
    """
    Input Variables: results_df (dataframe), standings_df (dataframe), t1 (string), t2 (string), mode (string)
    Output Variables: winning team name (string)
    Purpose: Applies NFL-style tiebreakers to determine which team ranks higher, with 2 different modes for the type of tiebreaker
    Example: tie_break(results_df, standings_df, "Ravens", "Bengals", mode="wildcard"), there is also functionalty for total_margin
    # and capped_margin for tiebreakers
    """
    valid_modes = {"division", "wildcard", "total_margin", "capped_margin"}
    if mode not in valid_modes:
        raise ValueError("mode must be one of: 'division', 'wildcard', 'total_margin', 'capped_margin'")

    fpi_1 = standings_df.loc[standings_df["Team"] == t1, "FPI"].iloc[0]
    fpi_2 = standings_df.loc[standings_df["Team"] == t2, "FPI"].iloc[0]

    if fpi_1 > fpi_2:
        higher_fpi = t1
    else:
        higher_fpi = t2

    w1 = nfl_win_pct(standings_df,t1)
    w2 = nfl_win_pct(standings_df,t2)
    
    if w1 > w2:
        return t1, "win percentage diff", fpi_result(t1,higher_fpi)
    if w2 > w1:
        return t2, "win percentage diff", fpi_result(t2,higher_fpi)

    # 1) head-to-head
    w = head_to_head(results_df, t1, t2)
    if w is not None:
        if mode == "division" or mode == "wildcard":
            return w, "head to head", fpi_result(w,higher_fpi)

    # 2) division record (division winner ties only)
    # division tiebreakers use division record and prioritize common games over conference record
    if mode == "division":
        w = division_record(standings_df, t1, t2)
        if w is not None:
            return w, "division_record", fpi_result(w,higher_fpi)
        w = common_games(results_df, t1, t2)
        if w is not None:
            return w, "common_games", fpi_result(w,higher_fpi)
        w = conference_record(standings_df, t1, t2)
        if w is not None:
            return w, "conference_record", fpi_result(w,higher_fpi)

        w1 = strength_of_victory(results_df, standings_df, t1)
        w2 = strength_of_victory(results_df, standings_df, t2)

        if w1 > w2:
            return t1, "strength_of_victory", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_victory", fpi_result(t2,higher_fpi)

        w1 = strength_of_schedule(results_df, standings_df, t1)
        w2 = strength_of_schedule(results_df, standings_df, t2)

        if w1 > w2:
            return t1, "strength_of_schedule", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_schedule", fpi_result(t2,higher_fpi)

    # 3) wildcard    
    #wildcard tiebreaker prioritizes conference record over conference games
    if mode == "wildcard":
        w = conference_record(standings_df, t1, t2)
        if w is not None:
            return w, "conference_record", fpi_result(w,higher_fpi)
        w = common_games(results_df, t1, t2)
        if w is not None:
            return w, "common_games", fpi_result(w,higher_fpi)

        w1 = strength_of_victory(results_df, standings_df, t1)
        w2 = strength_of_victory(results_df, standings_df, t2)

        if w1 > w2:
            return t1, "strength_of_victory", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_victory", fpi_result(t2,higher_fpi)

        w1 = strength_of_schedule(results_df, standings_df, t1)
        w2 = strength_of_schedule(results_df, standings_df, t2)

        if w1 > w2:
            return t1, "strength_of_schedule", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_schedule", fpi_result(t2,higher_fpi)

    # Total Margin
    # just looks at the point differential for each team
    if mode == "total_margin":
        
        tm1 = standings_df.loc[standings_df["Team"] == t1, "Total_Margin"].iloc[0]
        tm2 = standings_df.loc[standings_df["Team"] == t2, "Total_Margin"].iloc[0]
    
        if tm1 > tm2:
            return t1, "total_margin", fpi_result(t1, higher_fpi)
        elif tm2 > tm1:
            return t2, "total_margin", fpi_result(t2, higher_fpi)
        
        w1 = strength_of_victory(results_df, standings_df, t1)
        w2 = strength_of_victory(results_df, standings_df, t2)
        
        if w1 > w2:
            return t1, "strength_of_victory", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_victory", fpi_result(t2,higher_fpi)

    # Capped Margin
    # looks at the point differential for each team, but each and every game has a "cap", so a blowout doesn't skew the results
    if mode == "capped_margin":
        
        tm1 = standings_df.loc[standings_df["Team"] == t1, "Capped_Margin"].iloc[0]
        tm2 = standings_df.loc[standings_df["Team"] == t2, "Capped_Margin"].iloc[0]
    
        if tm1 > tm2:
            return t1, "capped_margin", fpi_result(t1, higher_fpi)
        elif tm2 > tm1:
            return t2, "capped_margin", fpi_result(t2, higher_fpi)
            
        w1 = strength_of_victory(results_df, standings_df, t1)
        w2 = strength_of_victory(results_df, standings_df, t2)
        
        if w1 > w2:
            return t1, "strength_of_victory", fpi_result(t1,higher_fpi)
        elif w2 > w1:
            return t2, "strength_of_victory", fpi_result(t2,higher_fpi)

    rng = np.random.default_rng()
    print("Coin flip! Between", [t1, t2])
    winner = rng.choice([t1, t2])
    return winner, "Coin Flip!", fpi_result(winner, higher_fpi)

# Name: division_winners
def division_winners(standings_df,results_df,tie_breakers,fpi_winners,mode = "default"):
    """
    Input Variables: standings_df (dataframe), results_df (dataframe)
    Output Variables: div_winners (dataframe) 
    Purpose: Determines the winner of each division using wins and division tiebreakers, then assigns seeds 1–4 within each conference
    Example: division_winners(standings_df, results_df)
    """
    if mode == "default":
        mode = "division"
        mode2 = "wildcard"
    else:
        mode2 = mode
    df = standings_df.copy()
    winners_rows = []

    for div, grp in df.groupby("Division"): # for loop goes division by division 
        max_wins = grp["Wins"].max() #takes the top team in the divison we're looking at by wins
        tied = grp[grp["Wins"] == max_wins]["Team"].tolist() #spits out a list of teams that are tied

        if len(tied) == 1: # if the list is only 1, then no one is tied via wins
            winner = tied[0]
        else:
            team1 = tied[0] # Assign the first team as the "king of the hill"
            for team2 in tied[1:]: # for every team that has a tied record
                team1, method, fpi = tie_break(results_df, df, team1, team2, mode=mode) # break the tie between the "king" and the iterated team.
                #whoever wins is the "new king".
                tie_breakers.append(method)
                fpi_winners.append(fpi)
            winner = team1

        winners_rows.append(grp[grp["Team"] == winner].iloc[0].to_dict())
    winners_rows = pd.DataFrame(winners_rows)
    seeded_rows = []

    for conf, grp in winners_rows.groupby("Conference"): # does conferences seperately
        remaining = grp.copy() # makes a copy of our divison winners and creates the remaining pool
        winners = [] # empty array to fill

        while len(winners) < 4:
            max_wins = remaining["Wins"].max() # 
            tied = remaining.loc[remaining["Wins"] == max_wins, "Team"].tolist()

            if len(tied) == 1:
                winner = tied[0]
            else:
                team1 = tied[0]
                for team2 in tied[1:]:
                    team1, method, fpi = tie_break(results_df, df, team1, team2, mode=mode2)
                    tie_breakers.append(method)
                    fpi_winners.append(fpi)
                winner = team1

            winners.append(winner)
            remaining = remaining[remaining["Team"] != winner]

        for team in winners:
            seeded_rows.append(grp[grp["Team"] == team].iloc[0].to_dict())

    div_winners = pd.DataFrame(seeded_rows)
    
    div_winners["Seed"] = div_winners.groupby("Conference").cumcount() + 1

    return div_winners[["Conference", "Seed", "Team", "Division", "Wins", "Losses", "Ties"]].reset_index(drop=True), tie_breakers, fpi_winners

# Name: wild_card
def wild_card(standings_df, results_df, div,tie_breakers,fpi_winners, mode = "default"):
    """
    Input Variables: standings_df (dataframe), results_df (dataframe)
    Output Variables: wildcards_df (dataframe)
    Purpose: Selects the three Wild Card teams per conference using wins and Wild Card tiebreakers, then assigns seeds 5–7 within each conference
    Example: wild_card(standings_df, results_df)
    """
    df = standings_df.copy()

    # Remove division winners from wildcard pool
    wc_pool = df[~df["Team"].isin(div["Team"])].copy()

    wildcard_rows = []
    if mode == "default":
        mode = "wildcard"
        mode2 = "division"
    else:
        mode2 = mode
    # Do AFC / NFC seperate
    for conf, grp in wc_pool.groupby("Conference"):

        remaining = grp.copy() #This is basically our pool of contenders for a wildcard spot
        winners = [] #This is an empty arrray to store teams that make the playoffs

        while len(winners) < 3:

            max_wins = remaining["Wins"].max() #Look at who has the most wins in our remaining group
            tied = remaining[remaining["Wins"] == max_wins]["Team"].tolist() #See if any other teams have the same record

            
            if len(tied) == 1: # If there's no teams tied, then add this team to our winner pool
                winner = tied[0]
            else:
                team1 = tied[0] # Assign the first team as the "king of the hill"
                for team2 in tied[1:]: # for every team that has a tied record
                    if df.loc[df["Team"] == team1, "Division"].iloc[0] != df.loc[df["Team"] == team2, "Division"].iloc[0]:
                        team1, method, fpi = tie_break(results_df, df, team1, team2, mode=mode)
                        # break the tie between the "king" and the iterated team.
                        tie_breakers.append(method)
                        fpi_winners.append(fpi)
                    else:
                        team1, method, fpi = tie_break(results_df, df, team1, team2, mode=mode2)
                        tie_breakers.append(method)
                        fpi_winners.append(fpi)
                winner = team1

            winners.append(winner) #add the winner to wild card group

            remaining = remaining[remaining["Team"] != winner] # Remove winner from remaining pool

        # Save rows
        for team in winners:
            wildcard_rows.append(grp[grp["Team"] == team].iloc[0].to_dict())

    wildcards_df = pd.DataFrame(wildcard_rows)

    # Assign seeds 5–7 within each conference
    wildcards_df["Seed"] = wildcards_df.groupby("Conference").cumcount() + 5

    return wildcards_df[["Conference", "Seed", "Team", "Division", "Wins", "Losses", "Ties"]].reset_index(drop=True), tie_breakers, fpi_winners

# Name: playoff_field
def playoff_field(standings_df,results_df, mode = "default"):
    """
    Input Variables: standings_df (dataframe), results_df (dataframe)
    Output Variables: field (dataframe)
    Purpose: Combines division winners and wild card teams into a complete playoff field
    Example: playoff_field(standings_df, results_df)
    """
    tie_breakers = []
    fpi_winners = []
    div, tie_breakers, fpi_winners = division_winners(standings_df, results_df, tie_breakers, fpi_winners,mode)
    wc,  tie_breakers, fpi_winners = wild_card(standings_df, results_df, div, tie_breakers, fpi_winners,mode)

    field = pd.concat([div, wc], ignore_index=True)
    field = field.sort_values(["Conference", "Seed"]).reset_index(drop=True)
    return field, tie_breakers,fpi_winners

