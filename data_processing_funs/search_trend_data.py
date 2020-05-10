import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def get_google_trends(country_code):
    """
    get designated country's google trend data
    :param country_code: ISO alpha_2
    :return: google trend data frame
    """
    from pytrends.request import TrendReq
    pytrend = TrendReq()
    keywords = ['coronavirus']
    pytrend.build_payload(kw_list=keywords, timeframe='today 3-m', geo=country_code)
    # get past 3 month of trend from today
    # search more than three month will return weekly accumulated results
    # data storing needed
    df = pytrend.interest_over_time()
    df = pd.DataFrame(df)
    return df


def trend_data_clean(country_code):
    """
    clean the google trend data frame to meet requirement
    only date and trend index will remain
    :param country_code:
    :return: a data frame with 2 columns: date, search trend index
    """
    df = get_google_trends(country_code)
    df2 = df.iloc[:, 0:1]
    df2.columns = ['_'.join([country_code, 'search'])]  # add country_code prefix to column name
    return df2


def merge_trend_data():
    """
    merge each country's google trend data and merge to a whole data frame
    :return: a data frame with rows as each date and columns as countries
    """
    import time
    path = 'data/current_countries.csv'
    country_table = pd.read_csv(path, keep_default_na=False)
    # create a base data frame using 'CN' data (to get date column)
    df = trend_data_clean('CN')
    for i in country_table['Code']:
        if i == 'CN':
            pass
        else:
            try:
                # get google trend data
                df2 = trend_data_clean(i)
                df = pd.merge(df, df2, how='left', left_index=True, right_index=True)
                time.sleep(3)
                print(i, "'s Search Trend appended")
            except:
                # if one country has no value, then fill NAs
                i2 = '_'.join([i, 'search'])
                df2 = pd.DataFrame(columns=[i2])
                df2[i2] = df2[i2].append(pd.Series(np.nan for _ in range(len(df))))
                df = pd.merge(df, df2, how='left', left_index=True, right_index=True)
                time.sleep(3)
                print(i, " has no value, NA filled")
    # this data frame requires update by
    # merge Chinese search trend data (baidu_trend from alt_data_sources)
    # for that Google is blocked in China and Baidu is the main search engine there
    df = df.reset_index()
    return df


# # driver codes
# search_trend = merge_trend_data()
# search_trend.to_csv('data/search_trends_20200424.csv', index=False)

# # test
# US_search = trend_data_clean('US')
# CN_search = trend_data_clean('CN')
#
# test = pd.concat([US_search, CN_search], axis=1)
# test.columns = ['US_search', 'CN_search']
#
# plt.cla()
# test.loc[:, ['US_search', 'CN_search']].plot()

# test.to_csv('temp/data/searchTrend_20200420.csv')