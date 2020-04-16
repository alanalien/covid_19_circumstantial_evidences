import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

path = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
file1 = "time_series_covid19_confirmed_global.csv"
file2 = "time_series_covid19_deaths_global.csv"
file3 = "time_series_covid19_recovered_global.csv"

confirmed = pd.read_csv(path + file1)
death = pd.read_csv(path + file2)
recovered = pd.read_csv(path + file3)


def date_formatting(df):  # rename columns by date
    from datetime import datetime
    sub_df = df.iloc[:, 1:]
    for i in range(0, len(sub_df.columns)):
        if i <= 2:
            pass
        else:
            date_string = sub_df.columns[i]
            d1 = datetime.date(datetime.strptime(date_string, '%m/%d/%y'))
            d2 = str(d1)
            sub_df.rename(columns={date_string: d2}, inplace=True)
    return sub_df


def country_grouping(df):  # group values by country
    country_group = date_formatting(df)
    country_group.fillna(value=0, inplace=True)
    country_group = country_group.groupby(['Country/Region'])[country_group.columns[3:]].sum().reset_index()
    return country_group


def get_df_name(df):  # get data frame name for further usage
    df_name = [i for i in globals() if globals()[i] is df][0]
    # https://stackoverflow.com/questions/31727333/get-the-name-of-a-pandas-dataframe
    return df_name


def remodeling(df):  # transposing, column renaming, and date format converting
    new_df = country_grouping(df)
    df_name = get_df_name(df)
    new_df.rename(columns={'Country/Region': 'Date'}, inplace=True)
    new_df = new_df.set_index('Date').T  # Date and its value (string) became index
    new_df.index = pd.to_datetime(new_df.index)
    new_df.columns = new_df.columns.str.replace(' ', '')
    new_df.columns = new_df.columns.str.replace(',', '')
    new_df = new_df.add_suffix('_' + df_name)
    return new_df


test1 = confirmed[0:]
test1 = remodeling(test1)
# print(test1)
# print(test1.dtypes)

# for col in test1.columns:
#     print(col)

# this gives date value indexed with country

plt.cla()
test1.loc[:, ['China_test1', 'US_test1', 'Italy_test1']].plot()

# test2 = test1.loc[:, ['China_test1', 'US_test1', 'Italy_test1', 'Korea,South_test1']]
