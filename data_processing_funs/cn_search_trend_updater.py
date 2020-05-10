import pandas as pd


def cn_trend_updater():
    """
    update CN_search when needed, requires manual input
    :return: an updated baidu_trend data frame
    """
    import math
    cn = pd.read_csv('data_get/alt_data_sources/baidu_trend_num.csv')
    # cn = pd.read_csv('temp/data/baidu_trend_20200508.csv')  # use when human mistake occurs
    st = pd.read_csv('data/search_trends.csv')

    df = pd.DataFrame(st['date'])
    df2 = df.merge(cn, left_on='date', right_on='date', how='left')

    # iter over rows and detect NaN
    for i, r in df2.iterrows():
        # if NaN, meaning the date haven't been input
        # then calls to input
        if math.isnan(r['CN_search']) is True:
            print(r['date'] + ':')
            df2.loc[i, 'CN_search'] = input()
        # else pass
        else:
            pass
    return df2


def cn_trend_norm():
    df = pd.read_csv('data_get/alt_data_sources/baidu_trend_num.csv')
    # normalize baidu trend result
    df['CN_search'] = (df['CN_search'] / df['CN_search'].max() * 100).round()
    return df


# # driver codes:
# cn_trend_num = cn_trend_updater()
# cn_trend_num.to_csv('data_get/alt_data_sources/baidu_trend_20200508.csv', index=False)
#
# cn_trend = cn_trend_norm()
# cn_trend.to_csv('data_get/alt_data_sources/baidu_trend.csv', index=False)