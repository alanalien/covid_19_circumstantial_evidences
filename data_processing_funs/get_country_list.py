import pandas as pd
import numpy as np
from data_processing_funs import covid_cases_data as ccd


# Get Country List
"""
get countries
"""


def get_current_countries():
    """
    get a table of countries currently with confirmed covid-19 cases
    :return: a data frame with country name and ISO alpha_2 codes
    """
    confirmed = ccd.covid_data_get('confirmed')
    country_table_path2 = 'data_get/alt_data_sources/country_codes.csv'
    countries = pd.read_csv(country_table_path2)  # country table: names / alpha_2 codes

    country_table = pd.DataFrame(columns=['Code'])
    country_affected = []
    for i in confirmed.columns:
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

    # country_table.to_csv('data/country_table.csv')
    return country_table


# # driver codes
# current_countries = get_current_countries()
# current_countries.to_csv('data/current_countries.csv', index=False)