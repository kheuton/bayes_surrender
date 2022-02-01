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

def get_weeks_in_year(year):
    """Given a year, return links to all weeks in that year.

    Args:
        year (int): Year to parse
    Returns
        [str]: List of string url's containing each week's schedule
    """

    # Get a link to the website for a given year
    season_url = f'https://www.pro-football-reference.com/years/{year}'
    r = requests.get(season_url)
    soup = BeautifulSoup(r.content, 'lxml')

    # Extract the link to every week of football for a given year, including playoffs
    week_links = soup.find_all("a", href=lambda href: href and "/week" in href)
    week_links = ['https://www.pro-football-reference.com' +week_link.get('href') for week_link in week_links]
    week_no_dup = list(set(week_links))

    return week_no_dup


def get_games_in_week(week_url):
    """Get links to all games in a given week.

    Args:
        week_url (str): Link to  season's schedule page on pro-football-reference
    Returns:
        [str]: List of URL's to every game
    """
    w = requests.get(week_url)
    week_soup = BeautifulSoup(w.content, 'lxml')

    # Extract the link to every game of football in a given week
    game_links = week_soup.find_all("a", href=lambda href: href and "/boxscores/201" in href)
    game_no_dup = list(set(game_links))

    game_links = ['https://www.pro-football-reference.com' + game.get('href') for game in game_no_dup]

    game_no_dup = list(set(game_links))

    return game_no_dup
