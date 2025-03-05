import numpy as np
import pandas as pd


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df
    if year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]
    if year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]
    if year != 'Overall' and country != 'Overall':
        temp_df = medal_df[(medal_df['Year'] == int(year)) & (medal_df['region'] == country)]

    if flag == 1:
        x = temp_df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year').reset_index()
    else:
        x = temp_df.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                      ascending=False).reset_index()

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']
    x['Gold'] = x['Gold'].astype('int')
    x['Silver'] = x['Silver'].astype('int')
    x['Bronze'] = x['Bronze'].astype('int')
    x['total'] = x['total'].astype('int')

    return x


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def data_over_time(df, col):
    """
    Calculates the number of unique values in a column over time (by Year).

    Parameters:
    df (DataFrame): The main DataFrame containing Olympic data.
    col (str): The column to analyze (e.g., 'region', 'Event', 'Name').

    Returns:
    DataFrame: A DataFrame with the count of unique values over time.
    """
    # Drop duplicates based on Year and the specified column
    data_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index()

    # Rename columns explicitly
    data_over_time.columns = ['Edition', col]

    # Sort by Edition (Year)
    data_over_time = data_over_time.sort_values('Edition').reset_index(drop=True)

    return data_over_time


def most_successful(df, sport):
    """
    Fetches the most successful athletes for a given sport.

    Parameters:
    df (DataFrame): The main DataFrame containing Olympic data.
    sport (str): The sport to filter by. 'Overall' for all sports.

    Returns:
    DataFrame: A DataFrame containing the most successful athletes and their medal counts.
    """
    # Filter data for athletes with medals
    temp_df = df.dropna(subset=['Medal'])

    # Filter by sport if not 'Overall'
    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    # Count medals per athlete and reset index
    medal_counts = temp_df['Name'].value_counts().reset_index()
    medal_counts.columns = ['Name', 'Medals']  # Rename columns explicitly

    # Merge with the original DataFrame to get additional details
    most_successful_df = medal_counts.head(15).merge(
        df[['Name', 'Sport', 'region']].drop_duplicates('Name'),
        on='Name',
        how='left'
    )

    return most_successful_df


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def most_successful_countrywise(df, country):
    """
    Fetches the top 10 most successful athletes for a given country.

    Parameters:
    df (DataFrame): The main DataFrame containing Olympic data.
    country (str): The country to filter by.

    Returns:
    DataFrame: A DataFrame containing the top 10 athletes and their medal counts.
    """
    # Filter data for the selected country and drop rows with missing medals
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    # Count the number of medals per athlete
    medal_counts = temp_df['Name'].value_counts().reset_index()
    medal_counts.columns = ['Name', 'Medals']  # Rename columns explicitly

    # Merge with the original DataFrame to get additional details
    top10_df = medal_counts.head(10).merge(
        df[['Name', 'Sport', 'region']].drop_duplicates('Name'),
        on='Name',
        how='left'
    )

    return top10_df


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final