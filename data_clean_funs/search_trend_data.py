import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# this function returns google trend of "coronavirus" in the past 3 month within a given country
def get_google_trends(country_code):
    """
    get selected country's google trend data
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


# TEST
# US_search = trend_data_clean('US')
# CN_search = trend_data_clean('CN')
#
# test = pd.concat([US_search, CN_search], axis=1)
# test.columns = ['US_search', 'CN_search']
#
# plt.cla()
# test.loc[:, ['US_search', 'CN_search']].plot()

# test.to_csv('temp/data/searchTrend_20200420.csv')


def merge_trend_data():
    import time
    path = 'data/country_table.csv'
    country_table = pd.read_csv(path, keep_default_na=False)
    # get CN data to create a base data frame
    df = trend_data_clean('CN')
    for i in country_table['Code']:
        if i == 'CN':
            pass
        else:
            try:
                df2 = trend_data_clean(i)
                df = pd.merge(df, df2, how='left', left_index=True, right_index=True)
                time.sleep(3)
                print(i, "'s Search Trend appended")
            except:
                i2 = '_'.join([i, 'search'])
                df2 = pd.DataFrame(columns=[i2])
                df2[i2] = df2[i2].append(pd.Series(np.nan for _ in range(len(df))))
                df = pd.merge(df, df2, how='left', left_index=True, right_index=True)
                time.sleep(3)
                print(i, " has no value, NA filled")
    return df


search_trend_data = merge_trend_data()
print(search_trend_data)

search_trend_data.to_csv('data/search_trends_20200503.csv')