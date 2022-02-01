import requests

import pandas as pd
from bs4 import BeautifulSoup
from bs4 import Comment

def get_punt_plays_from_df(play_df):
    """Filter down to just the punts"""
    punt_df = play_df.copy()

    # Filter out lines missing scores
    punt_df = punt_df[~punt_df.iloc[:,6].isna()]
    punt_df = punt_df[punt_df.iloc[:, 6].apply(lambda x: str(x).isdigit())]

    # Shift score down so its the score before the punt
    punt_df.iloc[:,6] = punt_df.iloc[:,6].shift(1)
    punt_df.iloc[:,7] = punt_df.iloc[:,7].shift(1)

    punt_df.loc[punt_df['Detail'].isna(), 'Detail'] = ''
    punt_df = punt_df[punt_df['Detail'].str.contains('punts')]

    # 50 yard line is handled weird
    punt_df.loc[punt_df['Location'].isna(), 'Location'] = f'{punt_df.columns[6]} 50'

    return punt_df

def get_losing_team(play_df):
    team_1 = play_df.columns[6]
    team_2 = play_df.columns[7]

    if play_df[team_1].values[-2] > play_df[team_2].values[-2] :
        return team_2
    elif play_df[team_2].values[-2]  > play_df[team_1].values[-2]:
        return team_1
    else:
        return None

def get_team_punters(punt_df, team):
    """Get a team's punters

    Args:
        punt_df (pd.DataFrame): Dataframe of kicking data with a Player column and Tm column
        team (str): 3-letter team abbrevation
    Returns:
        [str]: List of player names who could possibly punt for the team.
            Will include players who did not punt.
    """


    punters = punt_df[punt_df['Tm']==team.upper()].Player.unique()

    if len(punters)==0:
        raise ValueError('No punters found!')

    return punters

def assign_team_to_punts(punt_df, punters_df):
    """Given a dataframe of punt plays and another of each teams punters, assign a team to each play"""

    teams = punt_df.columns[6:8]
    if any([len(team)!=3 for team in teams]):
        raise ValueError(f'Unexpected teams {teams}')

    for team in teams:
        punters = get_team_punters(punters_df, team)

        # Assign team to punts based on who is kicking
        for punter in punters:
            punt_df.loc[punt_df['Detail'].str.startswith(punter), 'Tm'] = team

    if punt_df['Tm'].isna().any():
        raise ValueError(f'Missing team! {punt_df}')

    return punt_df
