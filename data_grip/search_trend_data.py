import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# this function returns google trend of "coronavirus" in the past 3 month within a given country
def get_google_trends(country_code):
    """ TO UPDATE:
    need an if clause to exclude Chinese search, to use Baidu data instead;
    need to output file and append results daily;
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
    df = get_google_trends(country_code)
    df2 = df.iloc[:, 0:1]
    df2.columns = ['_'.join([country_code, 'search'])]  # add country_code prefix to column name
    return df2


US_search = trend_data_clean('US')
CN_search = trend_data_clean('CN')

test = pd.concat([US_search, CN_search], axis=1)
test.columns = ['US_search', 'CN_search']

plt.cla()
test.loc[:, ['US_search', 'CN_search']].plot()
