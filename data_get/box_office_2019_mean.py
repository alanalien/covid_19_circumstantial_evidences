import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import re
import time
from data_clean_funs import box_office_data as bx


def box_office_2019_scraper(country_code):
    # url prams...
    url = "https://www.boxofficemojo.com/weekend/by-year/2019/?area="
    country_code = country_code  # argument: country code
    page = requests.get(url + country_code)
    soup = BeautifulSoup(page.content, 'html.parser')
    # create an empty data frame to hold country code info
    column_names = ["date",
                    "top_10_gross",
                    "top_10_last_week_compare",
                    "overall_gross",
                    "overall_last_week_compare",
                    "releases",
                    "#1_release",
                    "week"]
    box_office_table = pd.DataFrame(columns=column_names)

    # loop through all trs and append inside tds to country_code data frame as rows
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        td_list = [tds[0].text,
                   tds[1].text,
                   tds[2].text,
                   tds[3].text,
                   tds[4].text,
                   tds[5].text,
                   tds[6].text,
                   tds[10].text]
        # print(td_list)
        # new_row = pd.Series(td_list)
        box_office_table = box_office_table.append(
            pd.Series(td_list, index=box_office_table.columns),
            ignore_index=True
        )
    return box_office_table


def box_office_2019_cleaner(country_code):
    box_office_table = box_office_2019_scraper(country_code)  # call former function to scrape box office data
    box_office_table = box_office_table.iloc[:, [0, 3, 7]]  # select only useful columns

    # append formatted date column
    week_list = box_office_table.iloc[:, 2]  # get week number

    date_list = []
    for week_num in week_list:
        first_sunday = datetime.strptime('2019-01-06', '%Y-%m-%d')
        day_diff = (int(week_num)-1)*7
        new_date = first_sunday + timedelta(days=day_diff)
        new_date = datetime.date(new_date)
        date_list.append(new_date)

    box_office_table.insert(0, 'new_date', date_list, True)

    box_office_table = box_office_table.iloc[:, [0, 2]]
    box_office_table.columns = ['date', country_code]
    box_office_table = box_office_table.set_index(box_office_table['date'])
    box_office_table = pd.DataFrame(box_office_table)
    box_office_table = box_office_table.iloc[:, [1]]
    box_office_table = box_office_table.add_suffix('_boxOffice_total')
    return box_office_table


"""
BREAK
the following is an iteration that uses functions above,
which returns a data frame with total gross of all countries
listed on the mojo box office website
"""


def get_all_box_office_df():
    # call sunday_df() to create an empty data frame
    country_list = bx.mojo_country_codes()
    # loop through all country codes and scrape box office data
    for idx, my_codes in enumerate(country_list.loc[:, 'country_code']):
        # scrape each country's box office data
        box_office_data = box_office_2019_cleaner(my_codes)

        # clean box office data, make $449,007 format to int
        box_office_data_list = box_office_data.iloc[:, 0].tolist()
        box_office_num_list = []
        for usd in box_office_data_list:
            usd = usd[1:]
            usd = usd.replace(',', '')
            usd = int(usd)
            # print(usd)
            # append each int (box office total gross) to an empty list
            box_office_num_list.append(usd)
        # create a new column for the looping country
        # and insert the list of box office gross in
        box_office_data.insert(0, '_'.join([my_codes, 'boxOffice_usd']), box_office_num_list, True)
        # add the new column to the box office data frame
        box_office_df[my_codes + '_boxOffice_usd'] = box_office_data.iloc[:, [0]]

        print('done', my_codes, '------', idx, '/ 92')
        time.sleep(3)
    # remove the redundant date index
    box_office_df = box_office_df.reset_index(drop=True)
    return box_office_df


box_office_2019 = get_all_box_office_df()

