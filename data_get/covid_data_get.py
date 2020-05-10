import pandas as pd
from data_processing_funs import covid_cases_data as ccd
from data_processing_funs import get_country_list as cl
from data_processing_funs import box_office_data as bx, us_box_office_data as usbx
from data_processing_funs import box_office_yearly_mean as bx_mean
from data_processing_funs import search_trend_updater as stu
from data_processing_funs import cn_search_trend_updater as cnstu
from data_processing_funs import table_merge_stack as tms

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
box_office = bx.get_all_box_office_df(2020)
us_box_office = usbx.us_box_office_cleaner(2020)
box_office_full = pd.merge(box_office, us_box_office, left_on='date', right_on='date')
box_office_full.to_csv('data/box_office.csv', index=False)

# # get mean box office from Mojo data
# box_office_2019_mean = bx_mean.get_year_mean(2019)
# box_office_2019_mean.to_csv('data/box_office_2019_mean.csv', index=False)

# get search trend data
search_trend = stu.trend_update_output()
search_trend.to_csv('data/search_trends.csv', index=False)  # write out for cn_trend_updater
cn_search_trend_num = cnstu.cn_trend_updater()
cn_search_trend_num.to_csv('data_get/alt_data_sources/baidu_trend_20200508.csv', index=False)
cn_search_trend = cnstu.cn_trend_norm()
cn_search_trend.to_csv('data_get/alt_data_sources/baidu_trend.csv', index=False)
# replace search_trend's CN_search (google trend) with cn_search_trend (baidu trend)
search_trend['CN_search'] = cn_search_trend['CN_search']
search_trend.to_csv('data/search_trends.csv', index=False)

"""
stack data for viz
"""