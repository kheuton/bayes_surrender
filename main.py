"""Run all"""
import pandas as pd

from scraping_functions import get_table_from_game_comments, get_weeks_in_year, get_games_in_week
from parsing_functions import (get_punt_plays_from_df, get_team_punters,
                           assign_team_to_punts, get_losing_team)
from scoring_functions import (get_yrds_to_endzone, get_field_position_score,
                           get_yrds_to_go_score, get_gamescore_multilpier,
                           get_gameclock_multiplier, get_surrender_index)


if __name__ == '__main__':
    # Calculate Surrender index baseline
    baseline_punt_df = pd.DataFrame()
    error_games_base = []
    baseline_years = [2010, 2011, 2012, 2013, 2014]
    for year in baseline_years:
        week_urls = get_weeks_in_year(year)
        for week_url in week_urls:
            week = int(week_url.split('_')[1].split('.')[0])
            print(f'{year}, {week}')
            if year <2021:
                is_playoffs = week > 18
            else:
                is_playoffs = week > 17

            game_urls = get_games_in_week(week_url)

            for game_url in game_urls:
                try:
                    pbp_df = get_table_from_game_comments(game_url, 'pbp')
                    losing_team = get_losing_team(pbp_df)
                    punt_df = get_punt_plays_from_df(pbp_df)
                    punters_df = get_table_from_game_comments(game_url, 'kicking', header_row=1)
                    punt_df = assign_team_to_punts(punt_df, punters_df)
                    punt_df = get_yrds_to_endzone(punt_df)
                    punt_df = get_field_position_score(punt_df)
                    punt_df = get_yrds_to_go_score(punt_df)
                    punt_df = get_gamescore_multilpier(punt_df)
                    punt_df = get_gameclock_multiplier(punt_df, year, is_playoffs )
                    punt_df = get_surrender_index(punt_df)
                except ValueError:
                    # we lose some punts because punters names don't match
                    # i.e. Matt-> Matthew
                    error_games_base.append(game_url)
                    continue
                baseline_punt_df = baseline_punt_df.append(punt_df)

    print(f'{len(error_games_base)} could not be parsed')
    cowardly_punt_threshold = baseline_punt_df.surrender_index.quantile(0.9)
    print(f'Cowardly punt threshold is {cowardly_punt_threshold}')

    # Calculate bayesian stats
    games = 0
    losing_games = 0
    losing_games_with_cowardly_punts = 0
    games_with_cowardly_punts = 0
    error_games_test = []

    test_years = [2015, 2016, 2017, 2018, 2019]
    for year in test_years:
        week_urls = get_weeks_in_year(year)
        for week_url in week_urls:
            week = int(week_url.split('_')[1].split('.')[0])
            print(f'{year}, {week}')
            if year <2021:
                is_playoffs = week > 18
            else:
                is_playoffs = week > 17

            game_urls = get_games_in_week(week_url)

            for game_url in game_urls:
                try:
                    pbp_df = get_table_from_game_comments(game_url, 'pbp')
                    losing_team = get_losing_team(pbp_df)
                    punt_df = get_punt_plays_from_df(pbp_df)
                    punters_df = get_table_from_game_comments(game_url, 'kicking', header_row=1)
                    punt_df = assign_team_to_punts(punt_df, punters_df)
                    punt_df = get_yrds_to_endzone(punt_df)
                    punt_df = get_field_position_score(punt_df)
                    punt_df = get_yrds_to_go_score(punt_df)
                    punt_df = get_gamescore_multilpier(punt_df)
                    punt_df = get_gameclock_multiplier(punt_df, year, is_playoffs )
                    punt_df = get_surrender_index(punt_df)
                except ValueError:
                    error_games_test.append(game_url)
                    continue

                cowardly_punts = punt_df[punt_df['surrender_index']>cowardly_punt_threshold]

                # we're counting team-level stats here, so each game counts
                # once for each team
                games += 2
                if losing_team is not None:
                    losing_games += 1

                if len(cowardly_punts)>0:
                    games_with_cowardly_punts += len(cowardly_punts['Tm'].unique())

                    if losing_team in cowardly_punts['Tm'].unique():
                        losing_games_with_cowardly_punts += 1

    print(f'{len(error_games_test)} could not be parsed')
    print(f'Games played {games}')
    print(f'Losing games {losing_games}')
    print(f'Losing games with a cowardly punt: {losing_games_with_cowardly_punts}')
    print(f'Games with cowardly punts: {games_with_cowardly_punts}')
