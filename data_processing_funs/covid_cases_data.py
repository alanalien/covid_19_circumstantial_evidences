import pandas as pd
import numpy as np


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

def covid_data_get(type_to_get):  # type in ['confirmed', 'death', 'recovered'], case insensitive
    """
    driving data retriever,
    calls former functions to generate a cleaned covid data of designated type,
    i.e. confirmed/death/recovered
    data source from John Hopkins University COVID-19 data portal on GitHub
    :param type_to_get: i.e. confirmed/death/recovered
    :return: a data frame with date as index and countries (in ISO alpha_2 country code) as columns
    """
    type_to_get = str(type_to_get).lower()
    path = "https://raw.githubusercontent.com/" \
           "CSSEGISandData/COVID-19/master/" \
           "csse_covid_19_data/" \
           "csse_covid_19_time_series/"
    file1 = "time_series_covid19_confirmed_global.csv"
    file2 = "time_series_covid19_deaths_global.csv"
    file3 = "time_series_covid19_recovered_global.csv"
    file_to_get = ""
    if type_to_get == 'confirmed':
        file_to_get = file1
    elif type_to_get == 'death':
        file_to_get = file2
    elif type_to_get == 'recovered':
        file_to_get = file3
    else:
        print('data type not exist')

    df = pd.read_csv(path + file_to_get)
    df = remodeling(df, type_to_get)
    return df


# # driver codes:
# confirmed = covid_data_get('confirmed')
# death = covid_data_get('death')
# recovered = covid_data_get('recovered')

# # test
# import matplotlib.pyplot as plt
# plt.cla()
# confirmed.loc[:, :].plot(legend=None)
# death.loc[:, :].plot(legend=None)
# recovered.loc[:, :].plot(legend=None)

