import numpy as np
import pandas as pd
from itertools import combinations

# Name: add_game
# Input Variables: schedule (array), home team (string), away team (string), divisional (boolean), conference (boolean)
# Purpose: Allows customization to appending the schedule. For instance, flagging games as divisional matchups
# Example: add_game(schedule, a,b,divisional = True, conference = True)
def add_game(schedule, home, away, divisional=False, conference = False):
    schedule.append({"Home": home, "Away": away, "Divisional": divisional, "Conference": conference})

# Name: build_divisional_schedule
# Input Variables: division_teams (dict)
# Output Variables: schedule (array with home team, away team, divisional flag, conference flag)
# Purpose: Generates divisional matchups for all 8 divisions. Each team plays the 3 other teams in their conference 2 times. One away, one home
# Example: print(build_divisional_schedule({"NFC North": division_teams["NFC North"]}))
def build_divisional_schedule(division_teams):
    schedule = [] # This will store all games as (Home, Away)

    # For every pair of teams in the division
    for div_teams in division_teams.values():
        for a, b in combinations(div_teams, 2): 
            add_game(schedule, a,b,divisional = True, conference = True) # a home 
            add_game(schedule, b,a,divisional = True, conference = True) # b home
    return schedule

# Name: pair_up
# Input Variables: divs (list of strings), seed (int)
# Output Variables: pairs (array with division pairs)
# Purpose: Pairs up all inputed divisions together for cross-divisional matchups
# Example: print(pair_up(afc_divs,1)) | print(pair_up(nfc_divs,5))
def pair_up(divs,seed):
    rng = np.random.default_rng(seed) #Random number generator
    divs = list(divs) #List out all divisions
    rng.shuffle(divs) # Shuffle the divisions
    pairs = []

    for i in range(0, len(divs), 2): # Loop through the list two elements at a time
        pair = (divs[i], divs[i+1]) # Pair current division with the next one
        pairs.append(pair)
    return pairs

# Name: two_random_conference_games
# Input Variables: df (dataframe of NFL teams), schedule (array), pairs (array with division pairs), seed (int)
# Output Variables: schedule (array with home team, away team, divisional flag, conference flag)
# Purpose: Generates 2 matchups per team from inner-conference opponents not in their own division or the division they paired up with
# Example: schedule = two_random_conference_games(df, schedule, nfc_pairs, seed=1)

def two_random_conference_games(df, schedule, pairs, seed=1):
    rng = np.random.default_rng(seed)

    division_teams = df.groupby("Division")["Team"].apply(list).to_dict()
    #print(division_teams)
    (A, B) = pairs[0] # The first pair that was selected
    (C, D) = pairs[1] # The second pair that was selected

    division_1 = division_teams[A][:] # Teams from each division
    division_2 = division_teams[B][:]
    division_3 = division_teams[C][:]
    division_4 = division_teams[D][:]

    rng.shuffle(division_1) # Shuffle all teams in the divisions
    rng.shuffle(division_2)
    rng.shuffle(division_3)
    rng.shuffle(division_4)

    for i in range(4):
        a = division_1[i] 
        b = division_2[i]
        c = division_3[i]
        d = division_4[i]

        # Pair up 1 team from a with a team from division c and d
        add_game(schedule, a, c, divisional=False, conference=True) # Since A played B, A vs C will be a new matchup
        add_game(schedule, d, a, divisional=False, conference=True) # Same logic here
        
        # Pair up 1 team from b with a team from division c and d
        add_game(schedule, b, d, divisional=False, conference=True)
        add_game(schedule, c, b, divisional=False, conference=True)


    return schedule

# Name: one_random_other_conference
# Input Variables: df (dataframe of NFL teams), schedule (array), pairs (array with division pairs), seed (int)
# Output Variables: schedule (array with home team, away team, divisional flag, conference flag)
# Purpose: Generates 1 matchup per team from outer-conference opponents not in the division they paired up with
# Example: schedule = one_random_other_conference(df, schedule, cross_pairs, seed=1)

def one_random_other_conference(df, schedule, pairs, seed=1):
    rng = np.random.default_rng(seed)

    division_teams = df.groupby("Division")["Team"].apply(list).to_dict()

    # These basically represent every paired AFC and NFC division
    (A, B) = pairs[0]
    (C, D) = pairs[1] 
    (E, F) = pairs[2]
    (G, H) = pairs[3]

    # All the 2nd characters in the pair will be the AFC teams
    afc_list = [B,D,F,H]
    afc_copy = afc_list[:]

    while True: # This shuffles AFC teams so they HAVE to be in a new position in the list. Crucial for no repeat matchups
        # ie, if the AFC North is in position 3 in the list, they can't be in position 3 on the shuffle. As whatever NFC conference is playing 
        # the AFC North would play a team twice

        rng.shuffle(afc_list)
        diff_places = True
       
        for i in range(4): # This basically checks if the AFC conference is in a new position
            if afc_list[i] == afc_copy[i]:
                diff_places = False
                break
    
        if diff_places:
            break

    # A bit overkill here honestly
    nfc_division_1 = division_teams[A][:] # Teams from each division
    afc_division_1 = division_teams[afc_list[0]][:]
    nfc_division_2 = division_teams[C][:]
    afc_division_2 = division_teams[afc_list[1]][:]
    nfc_division_3 = division_teams[E][:]
    afc_division_3 = division_teams[afc_list[2]][:]
    nfc_division_4 = division_teams[G][:]
    afc_division_4 = division_teams[afc_list[3]][:]
    
    # Shuffle every single division in the NFL
    rng.shuffle(nfc_division_1)
    rng.shuffle(nfc_division_2)
    rng.shuffle(nfc_division_3)
    rng.shuffle(nfc_division_4)
    rng.shuffle(afc_division_1)
    rng.shuffle(afc_division_2)
    rng.shuffle(afc_division_3)
    rng.shuffle(afc_division_4)
    
    for i in range(4):
        a = nfc_division_1[i]
        b = afc_division_1[i]
        c = nfc_division_2[i]
        d = afc_division_2[i]
        e = nfc_division_3[i]
        f = afc_division_3[i]
        g = nfc_division_4[i]
        h = afc_division_4[i]
        
        if i % 2 == 0: #All unique match ups, the % 2 guarantees that half the division is at home, half is away
            add_game(schedule, a, b, divisional=False, conference=False)
            add_game(schedule, c, d, divisional=False, conference=False)
            add_game(schedule, e, f, divisional=False, conference=False)
            add_game(schedule, g, h, divisional=False, conference=False)
        else:
            add_game(schedule, b, a, divisional=False, conference=False)
            add_game(schedule, d, c, divisional=False, conference=False)
            add_game(schedule, f, e, divisional=False, conference=False)
            add_game(schedule, h, g, divisional=False, conference=False)

    return schedule

# Name: division_vs_division
# Input Variables: df (dataframe of NFL teams), schedule (array), d1 (division 1), d2 (division 2), seed (int)
# Output Variables: schedule (array with home team, away team, divisional flag, conference flag)
# Purpose: Generates 2 home and 2 away matchups for all teams between 2 divisions
# Example: print(division_vs_division(build_divisional_schedule({"NFC North": division_teams["NFC North"]})))
def division_vs_division(df, schedule, d1, d2,seed):
    rng = np.random.default_rng(seed)  # Random number

    division_teams = df.groupby("Division")["Team"].apply(list).to_dict()
    nfc_divs = [d for d in division_teams if d.split()[0] == "NFC"]
    afc_divs = [d for d in division_teams if d.split()[0] == "AFC"]

    A = division_teams[d1]  # Division 1
    B = division_teams[d2] # Division 2

    # Shuffling B for random home and away assignments
    B_perm = B[:] # Make a copy of B
    rng.shuffle(B_perm) # Shuffle the teams in B, this makes it so home/away assignments aren't the same every time

    conference = (d1.split()[0] == d2.split()[0])

    for i in range(4): # Loop through every team in division A
        a = A[i] # a = Current team in division A

        # These two teams will be hosted by team a
        home1 = B_perm[i] 
        home2 = B_perm[(i + 1)%4] # % 4 allows wrapping around if index reaches the end
        # So let's say Packers are team 4 in division a, they'd host team 4 and team 1 in division b
        # Loop through every team in division B
        for b in B:
            if b == home1 or b == home2:
                add_game(schedule, a, b, divisional=False, conference=conference)  # Team a is home vs team b
            else:
                add_game(schedule, b, a, divisional=False, conference=conference)  # Team b is home vs team a
    return schedule

# Name: generate_schedule
# Input Variables: df (dataframe of NFL teams), seed (int)
# Output Variables: schedule_df (data frame with home team, away team, divisional flag, conference flag)
# Purpose: Generates an entire 17 game NFL season for all 32 NFL teams
# Example: #schedule_df = generate_schedule(df, seed=4)
#print(schedule_df[(schedule_df["Home"] == "New England Patriots") |
                  #(schedule_df["Away"] == "New England Patriots")])
def generate_schedule(df: pd.DataFrame, seed: int = 1):

    rng = np.random.default_rng(seed)
    
    division_teams = df.groupby("Division")["Team"].apply(list).to_dict()
    nfc_divs = [d for d in division_teams if d.split()[0] == "NFC"]
    afc_divs = [d for d in division_teams if d.split()[0] == "AFC"]

    schedule = build_divisional_schedule(division_teams)
    
    # Divisional Schedule
    schedule = build_divisional_schedule(division_teams)

    # Pair up divisions
    nfc_pairs = pair_up(nfc_divs, seed)  # 2 pairs
    afc_pairs = pair_up(afc_divs, seed)  # 2 pairs
    
    # NFC Division matchups
    for d1, d2 in nfc_pairs:
        division_vs_division(df,schedule, d1, d2, seed)

    # AFC Division matchups
    for d1, d2 in afc_pairs:
        division_vs_division(df,schedule, d1, d2, seed)

    # NFC vs AFC matchup
    afc_shuf = afc_divs[:]  # Make a copy of AFC divisions
    rng.shuffle(afc_shuf) # Shuffle AFC divisions
    cross_pairs = list(zip(nfc_divs, afc_shuf))  # pairs up every division with each other
    for d1, d2 in cross_pairs:
        division_vs_division(df,schedule, d1, d2, seed)

    schedule = two_random_conference_games(df, schedule, nfc_pairs, seed=seed + 100)
    schedule = two_random_conference_games(df, schedule, afc_pairs, seed=seed + 200)
    schedule = one_random_other_conference(df, schedule, cross_pairs, seed=seed + 999)

    # converts schedule into a data frame
    schedule_df = pd.DataFrame(schedule, columns=["Home", "Away", "Divisional","Conference"])

    return schedule_df

