import pandas as pd
import numpy as np
import time
from datetime import date

import sys
# temporarily append the project directory to sys.path
# to allow the usage of the following modules
sys.path.append('/Users/wildgoose/PycharmProjects/covid_19_CE')

from data_processing_funs import covid_cases_data as ccd
from data_processing_funs import get_country_list as cl
from data_processing_funs import box_office_data as bx, us_box_office_data as usbx
from data_processing_funs import box_office_yearly_mean as bx_mean
from data_processing_funs import search_trend_updater as stu
from data_processing_funs import cn_search_trend_updater as cnstu
from data_processing_funs import table_merge_stack as tms
from data_processing_funs import covid_today as ctd

# timer
start_time = time.time()


"""
get all data and write to local
"""

# get JHU covid data
confirmed = ccd.covid_data_get('confirmed')
death = ccd.covid_data_get('death')
recovered = ccd.covid_data_get('recovered')
confirmed.to_csv('data/confirmed.csv', index=False)
death.to_csv('data/death.csv', index=False)
recovered.to_csv('data/recovered.csv', index=False)

# get current affected countries from JHU covid confirmed data
current_countries = cl.get_current_countries()
current_countries.to_csv('data/current_countries.csv', index=False)

# get box office from IMDB Mojo Box Office website
# only update on tuesdays to save run time
if date.today().weekday() == 1:  # whether today is tuesday
    box_office = bx.get_all_box_office_df(2020)
    us_box_office = usbx.us_box_office_cleaner(2020)
    box_office_full = pd.merge(box_office, us_box_office, left_on='date', right_on='date')
    box_office_full.to_csv('data/box_office.csv', index=False)
else:
    box_office_full = pd.read_csv('data/box_office.csv')
# box_office_full = pd.read_csv('data/box_office.csv')

# get mean box office from Mojo data
# box_office_2019_mean = bx_mean.get_year_mean(2019)  # no need to run unless error
# box_office_2019_mean.to_csv('data_get/alt_data_sources/box_office_2019_mean.csv', index=False)
box_office_2019_mean = pd.read_csv('data_get/alt_data_sources/box_office_2019_mean.csv')

# get search trend data
search_trend = stu.trend_update_output()
search_trend.to_csv('data/search_trends.csv', index=False)  # write out for cn_trend_updater
cn_search_trend_num = cnstu.cn_trend_updater()
cn_search_trend_num.to_csv('data_get/alt_data_sources/baidu_trend_num.csv', index=False)
cn_search_trend = cnstu.cn_trend_norm()
cn_search_trend.to_csv('data_get/alt_data_sources/baidu_trend.csv', index=False)
# replace search_trend's CN_search (google trend) with cn_search_trend (baidu trend)
search_trend['CN_search'] = cn_search_trend['CN_search']
search_trend.to_csv('data/search_trends.csv', index=False)
# search_trend = pd.read_csv('data/search_trends.csv')

"""
stack and manipulate data for viz
"""


def get_df_name(df):
    """
    get df name from environment
    acknowledgement:
    https://stackoverflow.com/questions/31727333/get-the-name-of-a-pandas-dataframe
    :param df: df to get name
    :return: df name string
    """
    name = [x for x in globals() if globals()[x] is df][0]
    return name


my_list = [confirmed, death, recovered, box_office_full, search_trend]


def merge_all(merge_list=my_list):
    """
    merge_all selected data frames
    and append derived columns
    :return: a data frame with all data for visualization
    """
    df = tms.transpose_for_altair(confirmed, 'confirmed')
    # reorder columns to simplify further steps
    df = df.iloc[:, [0, 2, 1]]
    # call easy_merge function to merge all data frames in the list
    for i in merge_list[1:]:  # skip 'confirmed'
        i_name = get_df_name(i)
        df_to_append = tms.transpose_for_altair(i, i_name)
        df = tms.easy_merge(df, df_to_append)
    # make all data numeric
    for i in df.iloc[:, 2:]:
        df[i] = pd.to_numeric(df[i])
    df = df.merge(box_office_2019_mean, left_on='country_code', right_on='country_code', how='left')
    # get additional information
    df['box_office_norm'] = df['box_office_full']/df['box_office_2019_mean']*100
    df['active_cases'] = df['confirmed']-df['death']-df['recovered']
    # add country_name
    current_countries.columns = ['country_code', 'country_name']
    df = df.merge(current_countries, left_on='country_code', right_on='country_code', how='left')
    country_info = pd.read_csv('data_get/alt_data_sources/country_info.csv')
    df = df.merge(country_info, left_on='country_code', right_on='country_code', how='left')
    # date to datetime
    df['date'] = pd.to_datetime(df['date'])
    return df


# driver codes
all_data = merge_all()
all_data.to_csv('data/all_data.csv', index=False)

covid_today = ctd.concat_data_today()
covid_today.to_csv('data/covid_today.csv', index=False)


# timer end
print("--- %s seconds ---" % (time.time() - start_time))
print('\n\n\n ################## covid data has been updated ################## \n\n\n')