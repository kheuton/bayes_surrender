import requests

import pandas as pd
from bs4 import BeautifulSoup
from bs4 import Comment


def get_table_from_game_comments(game_url, table_id, header_row=0):
    """Give the url of a game, return a dataframe hidden in the html comments

    For some reason, PFR hides tables in comment tags.
    This function extracts them

    Args:
        game_url (str): URL to game on pro-football-reference.com
        table_id (str): HTML id attribute for the desired table
        header_row (int): Option row of table header
    Returns:
        pd.DataFrame: Pandas dataframe of target table. Probably has messy rows
            from extra headers
    """
    r = requests.get(game_url)
    soup = BeautifulSoup(r.content, 'lxml')
    # ugh, table is hidden in a comment tag
    # Use this arcane magic to find all comment tags in html
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    for comment in comments:
        # Find the comment containing desired table
        if f'id="{table_id}"' in comment:
            # parse the contents of the comment
            comment_soup = BeautifulSoup(comment, 'lxml')
            # find  table
            table = comment_soup.find('table', id=table_id)

    # Use pandas to parse table html:
    df = pd.read_html(table.prettify(), header=header_row,
                      flavor='bs4' ,)[0]

    if len(df)==0:
        raise ValueError('No table found!')

    return df

def get_punt_plays_from_df(play_df):
    """Filter down to just the punts"""
    return play_df[play_df['Detail'].str.contains('punts')]

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
