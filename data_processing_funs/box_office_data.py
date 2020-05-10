import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import re
import time

"""
URL PARAMETER SCRAPER
"""


def mojo_country_codes():
    """
    get country codes that being used on mojo
    :return: df of mojo country codes
    """
    main_url = 'https://www.boxofficemojo.com/intl/?ref_=bo_nb_wew_tab'
    main_page = requests.get(main_url)
    main_soup = BeautifulSoup(main_page.content, 'html.parser')

    country_list = []
    code_list = []

    for select in main_soup.find_all('select')[0:]:
        option = select.find_all('option')
        for i in option:
            # print(i['value'], i.text)
            match = re.findall('(?<==).*$', i['value'])  # (?<=\=) positively look for characters behind '\='
            code = ''.join(match)
            name = i.text
            country_list.append(name)
            code_list.append(code)

    mojo_countries = pd.DataFrame({'country_name': country_list, 'country_code': code_list})
    mojo_countries.drop(mojo_countries[mojo_countries['country_code'] == 'FOREIGN'].index, inplace=True)
    return mojo_countries


"""
PAGE SCRAPER
"""


def box_office_scraper(country_code, year=2020):
    """
    scrape box office data of defined country and year
    :param country_code: country to scrap, in mojo country code (mostly in ISO alpha 2)
    :param year: year to scrap, default 2020
    :return: df of box office data
    """
    # url prams...
    year = str(year)
    main = "https://www.boxofficemojo.com/weekend/by-year/"
    country_code = country_code  # argument: country code
    url = main + year + '/?area=' + country_code
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # create an empty data frame to hold country code info
    column_names = ["Date",
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


# create empty data frame with sundays as index
def last_sunday(today):
    today = datetime.date(today)
    # if today is sunday return today
    if today.weekday() == 6:  # 6 means sunday
        sunday = today
    # otherwise get last sunday
    else:
        # see https://stackoverflow.com/questions/18200530/get-the-last-sunday-and-saturdays-date-in-python
        d = today.toordinal()
        sunday = d - (d % 7)
        sunday = datetime.date(datetime.fromordinal(sunday))
    return sunday


def sunday_df(year=2020):
    """
    get a data frame of all (past) sundays of the input year
    :param year: default 2020
    :return: df of all (past) sundays
    """
    year = int(year)
    sundays = []
    # get an input today if the year is 2020
    if year == 2020:
        today = datetime.now()
    # else get the last day of the designate year
    else:
        today = datetime.strptime((str(year)+"-12-31"), '%Y-%m-%d')
    # get last sunday result using to input today
    last_sunday_result = last_sunday(today)
    week_num = int((int(today.strftime('%j')) / 7)-1)  # %j represent the day of the year
    w = -1
    while w <= week_num:
        sundays.append(last_sunday_result - timedelta(w*7))
        w = w+1
        # print(w)
    df = pd.DataFrame(sundays, columns=['date'])
    df = df.drop(0).reset_index(drop=True)
    return df


def box_office_cleaner(country_code, year=2020):
    """
    clean the mojo box office data tables for further usage
    :param country_code: country to scrap, in mojo country code (mostly in ISO alpha 2)
    :return: df of only date and box office total gross
    """
    year = int(year)
    box_office_table = box_office_scraper(country_code=country_code, year=year)  # call former function to scrape box office data
    box_office_table = box_office_table.iloc[:, [0, 3, 7]]  # select only useful columns

    dates = sunday_df(year).reset_index()
    # the following line modifies the new index column by
    # 1. +1 to each number
    # 2. reverse the Series by [::-1]
    dates['week'] = (dates['index'] + 1)[::-1].reset_index(drop=True)
    box_office_table['week'] = pd.to_numeric(box_office_table['week'])
    box_office_table = pd.merge(box_office_table, dates, left_on='week', right_on='week')

    box_office_table = box_office_table.iloc[:, [4, 1]]
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


def get_all_box_office_df(year=2020):
    # call sunday_df() to create an empty data frame
    box_office_df = sunday_df(year)
    box_office_df = box_office_df.set_index(box_office_df['date'])
    # call mojo_country_codes() to get mojo's country list
    country_list = mojo_country_codes()
    # loop through all country codes and scrape box office data
    for idx, my_codes in enumerate(country_list.loc[:, 'country_code']):
        # scrape each country's box office data
        box_office_data = box_office_cleaner(my_codes, year=year)

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
    box_office_df['date'] = pd.to_datetime(box_office_df['date'])
    return box_office_df


