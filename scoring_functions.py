def get_yrds_to_endzone(punt_df):
    """Given a dataframe of punts with team assigned, extract yards to the endzone"""
    if 'Tm' not in punt_df.columns:
        raise ValueError('No team found, please add teams to dataframe of punts')

    punt_df.loc[:, 'field_side'] = punt_df['Location'].str.split(' ').apply(lambda x: x[0])
    punt_df.loc[:, 'yard_start'] = punt_df['Location'].str.split(' ').apply(lambda x: x[1]).astype(int)
    punt_df.loc[:,'yrds_to_endzone'] =  (punt_df['Tm']==punt_df['field_side'])*(100-2*punt_df['yard_start']) +\
                                         punt_df['yard_start']

    return punt_df

def get_field_position_score(punt_df):
    """Given a punt dataframe, calculate the field position component of surrender index"""

    if 'yrds_to_endzone' not in punt_df.columns:
        raise ValueError('Missing yards to endzone, please add this to dataframe first')

    # If in own teritory, score is 1 + 10% for each yard after 40
    own_filter = punt_df['yrds_to_endzone']>=50
    own_function = lambda yrds: max(1, 1.1**((100-yrds)-40))
    punt_df.loc[own_filter, 'field_pos_score'] = punt_df.loc[own_filter,
                                                            'yrds_to_endzone'].apply(own_function)

     # In opponent territory, score goes up 20% per yard
    opp_filter = punt_df['yrds_to_endzone']<50
    opp_function = lambda yrds: (1.2)**(50 - yrds) * ((1.1)**(10))
    punt_df.loc[opp_filter, 'field_pos_score'] = punt_df.loc[opp_filter,
                                                            'yrds_to_endzone'].apply(opp_function)

    return punt_df

def get_yrds_to_go_score(punt_df):
    """Calculate the yards to make 1st down discount of surrender index"""
    punt_df.loc[:, 'ToGo'] = punt_df['ToGo'].astype(int)

    # If its hard to get a first down, surrender index goes down
    punt_df.loc[punt_df['ToGo']>=10, 'to_go_discount'] = 0.2
    punt_df.loc[punt_df['ToGo']<10, 'to_go_discount'] = 0.4
    punt_df.loc[punt_df['ToGo']<6, 'to_go_discount'] = 0.6
    punt_df.loc[punt_df['ToGo']<4, 'to_go_discount'] = 0.8
    punt_df.loc[punt_df['ToGo']<2, 'to_go_discount'] = 1

    return punt_df

def get_gamescore_multilpier(punt_df):
    '''Calculate multiplier based on gamescore. If you're trailing by 1, go for it!'''

    teams = punt_df.columns[6:8]
    for team in teams:
        team_filter = punt_df['Tm']==team
        opp = [other_team for other_team in teams if other_team != team][0]

        # make scores ints
        punt_df.loc[:, team] = punt_df[team].astype(int)
        punt_df.loc[:, opp] = punt_df[opp].astype(int)

        punt_df.loc[team_filter, 'current_lead'] = punt_df.loc[team_filter, team] - punt_df.loc[team_filter, opp]

    # losing by 2+ scores multiplier = 3x
    punt_df.loc[punt_df['current_lead']<-8, 'score_multiplier'] = 3
    # losing by 1 score multiplier = 4x
    punt_df.loc[punt_df['current_lead']>=-8, 'score_multiplier'] = 4
    # Winning multiplier = 1
    punt_df.loc[punt_df['current_lead']>0, 'score_multiplier'] = 1
    # tied multiplier = 2
    punt_df.loc[punt_df['current_lead']==0, 'score_multiplier'] = 2

    return punt_df

def get_gameclock_multiplier(punt_df, year, is_playoffs):
    '''Only applies if tied or losing after halftime. Cubic function'''

    # replace OT with qt 5
    punt_df.loc[punt_df['Quarter']=='OT', 'Quarter'] = 5
    punt_df.loc[:,'Quarter'] =punt_df['Quarter'].astype(int)

    after_halftime_filter = punt_df['Quarter']>=3
    ot_filter = punt_df['Quarter']==5
    if is_playoffs:
        ot_length = 15
    else:
        if year <2017:
            ot_length = 15
        else:
            ot_length = 10

    losing_or_tied_filter = punt_df['current_lead'] <=0
    gameclock_filter = after_halftime_filter & losing_or_tied_filter

    punt_df.loc[:,'gameclock_minutes'] = punt_df['Time'].str.split(':').apply(lambda x: x[0]).astype(int)
    punt_df.loc[:,'gameclock_seconds'] = punt_df['Time'].str.split(':').apply(lambda x: x[1]).astype(int)

    punt_df.loc[:, 'seconds_since_halftime'] = 0
    punt_df.loc[after_halftime_filter, 'seconds_since_halftime'] = (punt_df.loc[after_halftime_filter,'Quarter']-3)*15*60 + \
                                                                   (15 - punt_df.loc[after_halftime_filter,'gameclock_minutes']-1) *60+ \
                                                                   (60-punt_df.loc[after_halftime_filter,'gameclock_seconds'])
    punt_df.loc[ot_filter, 'seconds_since_halftime'] = (punt_df.loc[ot_filter,'Quarter']-3)*15*60 + \
                                                                   (ot_length - punt_df.loc[ot_filter,'gameclock_minutes']-1) *60+ \
                                                                   (60-punt_df.loc[ot_filter,'gameclock_seconds'])
    punt_df.loc[:,'gameclock_multiplier'] = 1
    punt_df.loc[gameclock_filter, 'gameclock_multiplier'] = (punt_df.loc[gameclock_filter, 'seconds_since_halftime']*0.001)**3+1

    return punt_df

def get_surrender_index(punt_df):

    punt_df.loc[:,'surrender_index'] = punt_df['field_pos_score'] * punt_df['to_go_discount'] * punt_df['score_multiplier'] *  punt_df['gameclock_multiplier']

    return punt_df
