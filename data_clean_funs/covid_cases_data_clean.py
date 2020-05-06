import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def date_formatting(df):
    """
    turn dates in column names
    to yyyy-mm-dd format
    """
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
    """
    group data by country to
    absorb some data abnormally
    and make all data on the same geo level
    """
    country_group = date_formatting(df)
    country_group.fillna(value=0, inplace=True)
    country_group = country_group.groupby(['Country/Region'])[country_group.columns[3:]].sum().reset_index()
    return country_group


def country_code_update(df):
    """
    change the country names to ISO alpha_2 country code

    # all cruise ship cases have been removed
    # West Bank and Gaza region is considered as part of Palestine (PS)
    # Taiwan is considered separately from China here, for it has potentially different data collection procedure.
    # XK represents Kosovo (XK, XKX, while Kosovo is not listed as an ISO standard country.
    #   The unofficial 2 and 3-digit codes are used by the European Commission and others,
    #   until Kosovo is assigned an ISO code.
    """
    from pycountry import countries as ct
    new_df = country_grouping(df)
    # country names in the data set that are not fit ISO standard
    completion = pd.DataFrame(np.array([['Bolivia', 'BO'],
                                        ['Brunei', 'BN'],
                                        ['Congo (Brazzaville)', 'CG'],
                                        ['Congo (Kinshasa)', 'CD'],
                                        ['Cote d\'Ivoire', 'CI'],
                                        ['Holy See', 'VA'],
                                        ['Iran', 'IR'],
                                        ['Korea, South', 'KR'],
                                        ['Moldova', 'MD'],
                                        ['Russia', 'RU'],
                                        ['Taiwan*', 'TW'],
                                        ['Tanzania', 'TZ'],
                                        ['US', 'US'],
                                        ['Venezuela', 'VE'],
                                        ['Vietnam', 'VN'],
                                        ['Syria', 'SY'],
                                        ['Laos', 'LA'],
                                        ['West Bank and Gaza', 'PS'],
                                        ['Kosovo', 'XK'],
                                        ['Burma', 'MM']
                                        ]),
                              columns=['c_name', 'c_code']
                              )
    country_code_list = []
    for country_name in new_df['Country/Region']:
        try:
            if country_name in completion['c_name'].tolist():
                # print('exception covered: ', country_name)
                country_code = completion['c_code'].loc[completion['c_name'] == country_name].item()
            # identifies the cruise ships in the data set considered as a 'country'
            elif country_name == 'Diamond Princess' or country_name == 'MS Zaandam':
                country_code = 'Cruise Ship'
            else:
                country_code = ct.get(name=country_name).alpha_2
        except Exception:
            print('no result: ', country_name)
            country_code = 'None'
            pass
        country_code_list.append(country_code)
    # print(country_code_list)
    new_df.insert(0, "country_code", country_code_list, True)
    new_df = new_df.drop(columns='Country/Region')
    unknown_index = new_df[new_df['country_code'] == 'Cruise Ship'].index
    new_df.drop(unknown_index, inplace=True)  # drop when country_code = 'None', most likely are Cruise ships
    # new_df.set_index(new_df['country_code'])
    return new_df


# This won't work when being called
# def get_df_name(df):  # get data frame name for further usage
#     df_name = [i for i in globals() if globals()[i] is df][0]
#     # https://stackoverflow.com/questions/31727333/get-the-name-of-a-pandas-dataframe
#     return df_name
# So add new argus 'df_name' here to replace


def remodeling(df, df_name):
    """
    transposing, column renaming,
    and date format converting
    :return: 2 dimension covid data
        - variables: country
        - observations: counts, by day
        - table: confirmed/death/recovered, depending on input df
    """
    # df_name = get_df_name(df)
    new_df = country_code_update(df)
    new_df.rename(columns={'country_code': 'Date'}, inplace=True)
    new_df = new_df.set_index('Date').T  # Date and its value (string) became index
    new_df.index = pd.to_datetime(new_df.index)
    new_df = new_df.add_suffix('_' + df_name)
    # new_df.set_index(new_df['Date'])
    return new_df


# TEST:


# driver codes:

path = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
file1 = "time_series_covid19_confirmed_global.csv"
file2 = "time_series_covid19_deaths_global.csv"
file3 = "time_series_covid19_recovered_global.csv"

confirmed = pd.read_csv(path + file1)
death = pd.read_csv(path + file2)
recovered = pd.read_csv(path + file3)

CF = remodeling(confirmed, 'confirmed')
DT = remodeling(death, 'death')
CU = remodeling(recovered, 'CU')

# plt.cla()
# CF.loc[:, :].plot(legend=None)
# DT.loc[:, :].plot(legend=None)
# CU.loc[:, :].plot(legend=None)


# Get Country List
"""
get countries
"""

country_table_path2 = 'data/country_codes.csv'
countries = pd.read_csv(country_table_path2)  # country table: names / alpha_2 codes

country_table = pd.DataFrame(columns=['Code'])
country_affected = []
for i in CF.columns:
    country_affected.append(i[:2])

country_table['Code'] = country_table['Code'].append(pd.Series(country_affected), ignore_index=True)
country_table = pd.merge(country_table, countries, how='left', left_on='Code', right_on='Code')

# country_table[country_table['Name'].isnull() == True]
# #     Code Name
# # 90    XK  NaN
# # 116   NA  NaN

# XK = Kosovo, NA = Namibia
# Manually insert
country_table.loc[country_table['Code'] == 'XK', 'Name'] = 'Kosovo'
country_table.loc[country_table['Code'] == 'NA', 'Name'] = 'Namibia'

country_table.to_csv('data/country_table.csv')
"""
country_table might need update
when new countries have new coronavirus cases
"""

