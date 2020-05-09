import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from data_clean_funs import box_office_data as bx


def us_box_office_scraper(year=2020):
    # url prams...
    year = str(year)
    url = "https://www.boxofficemojo.com/weekend/by-year/" + year
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


def long_weekend_drop(df):
    """
    drop duplicated long weekend data
    :param df: df of mojo domestic box office by weekend
    :return: df without duplicated weekends
    """
    df = df.drop_duplicates(subset=['week'], keep='last')
    return df


def us_box_office_cleaner(year=2020):
    """
    clean mojo domestic box office data:
    1. keep only date, total_gross and week column
    :param year: default 2020
    :return:
    """
    df = us_box_office_scraper(year)
    df = long_weekend_drop(df)
    df = df.iloc[:, [0, 3, 7]]
    box_office_num_list = []
    for usd in df.iloc[:, 1]:
        usd = usd[1:]
        usd = usd.replace(',', '')
        usd = int(usd)
        box_office_num_list.append(usd)
    df.insert(0, 'US_boxOffice_usd', box_office_num_list, True)

    # add real dates
    # get all passed sundays and make it a data frame
    dates = bx.sunday_df(year).reset_index()
    # the following line modifies the new index column by
    # 1. +1 to each number
    # 2. reverse the Series by [::-1]
    dates['week'] = (dates['index']+1)[::-1].reset_index(drop=True)
    df['week'] = pd.to_numeric(df['week'])
    df = pd.merge(df, dates, left_on='week', right_on='week')
    df = df.drop(['Date', 'week', 'overall_gross', 'index'], axis=1)
    return df