# playoffs.py
import pandas as pd
import numpy as np

# Name: head_to_head
# Input Variables: results_df (dataframe), t1 (string, ie Football team), t2 (string, ie Football team)
# Output Variables: Will return the team that has the better record OR none if they've never played/have equal record
# Purpose: Looks at 2 teams and sees who has the better record against each other
# Example:
def head_to_head(results_df,t1,t2):
    games = results_df[((results_df["Home"] == t1) & (results_df["Away"] == t2)) |((results_df["Home"] == t2) & (results_df["Away"] == t1))].copy()
    # Above makes a copy of every matchup between the 2 teams

    if len(games) == 0: #if they have never play, return
        return None

    t1_wins = (games["Winner"] == t1).sum() #Add up the games where team 1 wins
    t2_wins = (games["Winner"] == t2).sum() #Add up the games where team 2 wins

    if t1_wins > t2_wins: 
        print(games)
        return t1
    if t2_wins > t1_wins:
        print(games)
        return t2
    return None

# Name: division_record
# Input Variables: standings_df (dataframe), t1 (string, ie Football team), t2 (string, ie Football team)
# Output Variables: team name (string) or None
# Purpose: Breaks ties using divisional wins
# Example: division_record(standings_df, "Packers", "Lions")
def division_record(standings_df,t1,t2):
    w1 = int(standings_df.loc[standings_df["Team"] == t1, "Div_Wins"].iloc[0])
    w2 = int(standings_df.loc[standings_df["Team"] == t2, "Div_Wins"].iloc[0])

    if w1 > w2:
        return t1
    if w2 > w1:
        return t2
    return None

# Name: conference_record
# Input Variables: standings_df (dataframe), t1 (string), t2 (string)
# Output Variables: team name (string) or None
# Purpose: Breaks ties using conference wins
# Example: conference_record(standings_df, "Eagles", "Cowboys")
def conference_record(standings_df,t1,t2):
    w1 = int(standings_df.loc[standings_df["Team"] == t1, "Conf_Wins"].iloc[0])
    w2 = int(standings_df.loc[standings_df["Team"] == t2, "Conf_Wins"].iloc[0])

    if w1 > w2:
        return t1
    if w2 > w1:
        return t2
    return None

# Name: common_games
# Input Variables: results_df (dataframe), t1 (string), t2 (string)
# Output Variables: team name (string) or None
# Purpose: Breaks ties using wins against common opponents
# Example: common_games(results_df, "49ers", "Seahawks")
def common_games(results_df, t1, t2):
    # Opponents each team played
    # set() function allows us to get a clean intersection
    t1_opponents = set(results_df.loc[results_df["Home"] == t1, "Away"]) | set(results_df.loc[results_df["Away"] == t1, "Home"])
    t2_opponents = set(results_df.loc[results_df["Home"] == t2, "Away"]) | set(results_df.loc[results_df["Away"] == t2, "Home"])

    # Common opponents (remove each other so head to head doesn't sneak in)
    common = (t1_opponents & t2_opponents) - {t1, t2}
    
    # NFL rule: must have at least 4 common opponents
    if len(common) < 4:
        print("Not enough opponents!", common)
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

#def stength_of_victory
#what is it? the average win total of the teams you beat

#def strength_of_schedule
#what is it? the average win total of the teams you played

#def combined_ranking_conference
#what is it? points for ranking + points against ranking amongst conference (1-16 for both)

#def combined_ranking_overall
#what is it? points for ranking + points against ranking amongst conference (1-32 for both)

#def net_points_common
#what is it? total points for vs total points against in common games

#def net_points_overall
#what is it? total points for vs total points against in all games

#def net_tds
#what is it? total TDs for vs total TDs against in all games

#def 
# Name: tie_break
# Input Variables: results_df (dataframe), standings_df (dataframe), t1 (string), t2 (string), mode (string)
# Output Variables: winning team name (string)
# Purpose: Applies NFL-style tiebreakers to determine which team ranks higher, with 2 different modes for the type of tiebreaker
# Example: tie_break(results_df, standings_df, "Ravens", "Bengals", mode="wildcard")
def tie_break(results_df, standings_df, t1, t2, mode="division"):
    rng = np.random.default_rng(10) # need to change this to seed
    # 1) head-to-head
    w = head_to_head(results_df, t1, t2)
    if w is not None:
        print(w, "won a tiebreaker by head to head") #I added all these print statements to see what tie break method is going through
        return w

    # 2) division record (division winner ties only)
    # division tiebreakers use division record and prioritize common games over conference record
    if mode == "division":
        w = division_record(standings_df, t1, t2)
        if w is not None:
            print(w, "won a tiebreaker by division_record")
            return w
            # 4) common games (later)
        w = common_games(results_df, t1, t2)
        if w is not None:
            print(w, "won a tiebreaker by common_games")
            return w
        w = conference_record(standings_df, t1, t2)
        if w is not None:
            print(w, "won a tiebreaker by conference_record")
            return w

    # 3) wildcard    
    #wildcard tiebreaker prioritizes conference record over conference games
    if mode == "wildcard":
        w = conference_record(standings_df, t1, t2)
        if w is not None:
            print(w, "won a tiebreaker by conference_record")
            return w
        w = common_games(results_df, t1, t2)
        if w is not None:
            print(w, "won a tiebreaker by common_games")
            return w

    print("Coin flip!", [t1, t2])
    return rng.choice([t1, t2])

# Name: division_winners
# Input Variables: standings_df (dataframe), results_df (dataframe)
# Output Variables: div_winners (dataframe) 
# Purpose: Determines the winner of each division using wins and division tiebreakers, then assigns seeds 1–4 within each conference
# Example: division_winners(standings_df, results_df)
# Things to fix: Seeding division winners (1–4) should use wild card tiebreakers when teams tie on wins
def division_winners(standings_df,results_df):

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
                team1 = tie_break(results_df, df, team1, team2, mode="division") # break the tie between the "king" and the iterated team.
                #whoever wins is the "new king".
            winner = team1

        winners_rows.append(grp[grp["Team"] == winner].iloc[0].to_dict())

    div_winners = pd.DataFrame(winners_rows)

    # seed 1-4 per conference, simply sort by wins
    # I need to replace this with a loop similar to the one in wild_card, that sorts the division winners with a wildcard tiebreaker
    div_winners = div_winners.sort_values(by=["Conference", "Wins", "Team"],ascending=[True, False, True]).reset_index(drop=True)
    
    div_winners["Seed"] = div_winners.groupby("Conference").cumcount() + 1

    return div_winners[["Conference", "Seed", "Team", "Division", "Wins", "Losses"]].reset_index(drop=True)

# Name: wild_card
# Input Variables: standings_df (dataframe), results_df (dataframe)
# Output Variables: wildcards_df (dataframe)
# Purpose: Selects the three Wild Card teams per conference using wins and Wild Card tiebreakers, then assigns seeds 5–7 within each conference
# Example: wild_card(standings_df, results_df)
# Things to fix: Division tiebreakers are actually used for brekaing a tie between 2 wildcard teams of the same division, so put an if-then for that
def wild_card(standings_df, results_df):
    df = standings_df.copy()

    # Remove division winners from wildcard pool
    div = division_winners(df, results_df)
    wc_pool = df[~df["Team"].isin(div["Team"])].copy()

    wildcard_rows = []

    # Do AFC / NFC seperate
    for conf, grp in wc_pool.groupby("Conference"):

        remaining = grp.copy() #This is basically our pool of contenders for a wildcard spot
        winners = [] #This is an empty arrray to store teams that make the playoffs

        # P
        while len(winners) < 3 and len(remaining) > 0:

            max_wins = remaining["Wins"].max() #Look at who has the most wins in our remaining group
            tied = remaining[remaining["Wins"] == max_wins]["Team"].tolist() #See if any other teams have the same record

            
            if len(tied) == 1: # If there's no teams tied, then add this team to our winner pool
                winner = tied[0]
            else:
                team1 = tied[0] # Assign the first team as the "king of the hill"
                for team2 in tied[1:]: # for every team that has a tied record
                    team1 = tie_break(results_df, df, team1, team2, mode="wildcard") # break the tie between the "king" and the iterated team.
                    #whoever wins is the "new king". What's nice about this is winners will be put in correct seeding order
                winner = team1

            winners.append(winner) #add the winner to wild card group

            remaining = remaining[remaining["Team"] != winner] # Remove winner from remaining pool

        # Save rows
        for team in winners:
            wildcard_rows.append(grp[grp["Team"] == team].iloc[0].to_dict())

    wildcards_df = pd.DataFrame(wildcard_rows)

    # Assign seeds 5–7 within each conference
    wildcards_df["Seed"] = wildcards_df.groupby("Conference").cumcount() + 5

    return wildcards_df[["Conference", "Seed", "Team", "Division", "Wins", "Losses"]].reset_index(drop=True)

# Name: playoff_field
# Input Variables: standings_df (dataframe), results_df (dataframe)
# Output Variables: field (dataframe)
# Purpose: Combines division winners and wild card teams into a complete playoff field
# Example: playoff_field(standings_df, results_df)
def playoff_field(standings_df,results_df):
    div = division_winners(standings_df,results_df)
    wc = wild_card(standings_df,results_df)

    field = pd.concat([div, wc], ignore_index=True)
    field = field.sort_values(["Conference", "Seed"]).reset_index(drop=True)
    return field

