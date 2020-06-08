import pandas as pd
import numpy as np

import sys
# temporarily append the project directory to sys.path
# to allow the usage of the following modules
sys.path.append('/Users/wildgoose/PycharmProjects/covid_19_CE')

from data_processing_funs import search_trend_data as st


def trend_updater(base_df, update_df):
    """
    this function concatenate new rows to the original search data frame (from 20200420);
    and tries to normalize the data
    :param base_df:
    :param update_df:
    :return: a concatenated data frame
    """
    base_df['date'] = base_df['date'].astype(str)
    update_df['date'] = update_df['date'].astype(str)
    base_df = base_df.set_index('date')
    update_df = update_df.set_index('date')

    for i in update_df:
        if i == 'CN_search':
            # China Search Trend is using alt data source, pass
            pass
        else:
            # from the data frame get index (date) with most searches
            # i.e. max(column.value)
            # and max value of google trend index must be 100
            update_max_dates = update_df.index[update_df[i] == 100].tolist()
            try:
                # get former_max_date
                # which holds the value from the former search trend data frame of the certain date
                # some countries might have more than one day reach the max search
                # use new_max_dates[0] to get the data out of the list and select only the first one
                my_date = update_max_dates[0]
                # find the value of my_date from base_df
                former_max_date_value = base_df.loc[my_date, i]

                # if former_max_date'value matches with max_date'value (i.e. = 100),
                # meaning google trend index doesn't need to reset
                if former_max_date_value == 100:
                    # then pass
                    """
                    to update: direct concat
                    """
                    pass
                # else former_max_date is less than 100, greater than doesn't exist
                # meaning the peak of search trend is in new data
                elif former_max_date_value < 100:
                    # get the last date from the base_df,
                    # which is an one-item-array obj from the index.values,
                    # use [0] to get the value
                    base_last_date = base_df.tail(1).index.values[0]
                    # get the iterating country's column from base_df and update_df
                    base_col = base_df[i]
                    update_col = update_df[i]
                    # recalculate the base_df of this country
                    fraction_base = base_col.loc[base_last_date]
                    fraction_update = update_col.loc[base_last_date]
                    # revalue the base_col
                    """
                    NOTE:
                    in some smaller countries, the data was enough and therefore the "fraction_base" becomes 0.
                    in that case NaN would generate.
                    The best workaround here would be find the nearest cell in columns
                    and use its index (date) to do this calculation.
                    but it would make this function extremely more complicate.
                    For the scope of this project, these countries are ignored here.
                    in the test, these countries are "Sao Tome and Principe" and "Eritrea".
                    """
                    base_col = round(base_col/fraction_base*fraction_update)
                    base_df[i] = base_col
                    # print(former_max_date_value, '\t\t', my_date)
                else:
                    print('look out!!' + '\t\t ==========\t' + i)
                    pass

            except KeyError:
                # there are two possibilities:
                # b. that the update_max_dates is out of the scope of base_df
                # i.e. later than base_last_date
                if i in base_df.columns:
                    # # get the last date from the base_df,
                    # # which is an one-item-array obj from the index.values,
                    # # use [0] to get the value
                    # base_last_date = base_df.tail(1).index.values[0]
                    # # get the iterating country's column from base_df and update_df
                    # base_col = base_df[i]
                    # update_col = update_df[i]
                    # # recalculate the update_df of this country
                    # fraction_base = base_col.loc[base_last_date]
                    # fraction_update = update_col.loc[base_last_date]
                    # # revalue the base_col
                    # base_col = round(base_col/fraction_base*fraction_update)
                    # base_df[i] = base_col
                    pass
                # a. if the country was new (i.e. not included in the former search trend data)
                else:
                    # create a new column in base data to hold it, fill NAs
                    base_df[i] = pd.Series(np.NaN, base_df.index)
                    print("new_country, NA filled \t\t ==========\t" + i)

            except IndexError:
                # index error occurs when google trend 'doesn't have enough data'
                print("not enough data \t\t\t ----------\t" + i)
                pass

    # reset index
    base_df = base_df.reset_index()
    update_df = update_df.reset_index()
    # concat the update_df to base_df, drop rows if date (index) is duplicated)
    # iter over rows of update_df
    for index, rows in update_df.iterrows():
        # if date is duplicated
        # find date in date column, since it's a series, use unique to determine
        date = rows[0]
        if date in base_df['date'].unique():
            # pass (ignore/drop it)
            pass
        # if not
        else:
            # add the row to the end of base_df
            base_df = base_df.append(rows, ignore_index=True)
    # reset the index to max = 100
    """
    NOTE:
    it seems that the calculation of google trend index is a bit more complicated,
    at their end,
    the "max value" might vary when new data was appended
    eg. For Ukraine, the query result on 20200508 shows the peak is at Mar 28th,
        while the result on 20200426 shows the peak at Apr 3rd,
        Although Apr 3rd still have a relatively high value (92),
        the difference still worth notice.
    for this reason, in the following block I reset the index on both conditions:
    max_value is greater or is smaller than 100, to make the index consistent.
    """
    # iter over each column (date column skipped),
    for i in range(1, len(base_df.columns)):
        my_col = base_df.iloc[:, i]
        max_value = max(my_col)
        # if max_value = 100, the data is valid, pass
        if max_value == 100:
            pass
        # else when max_value is > or < 100, reset the trend index
        else:
            # print(max_value)
            base_df.iloc[:, i] = round(my_col / max_value * 100)
    return base_df


def trend_update_output():
    # # read the earliest search trend data
    # base = pd.read_csv('data_get/alt_data_sources/search_trends_20200424.csv')
    # read last search trend data
    base = pd.read_csv('data/search_trends.csv')
    # call get search trend function
    new = st.merge_trend_data()
    # new = pd.read_csv('temp/data/search_trends_20200508.csv')
    trend_df = trend_updater(base, new)
    return trend_df


# # driver codes
# df = trend_update_output()
# df.to_csv('data/search_trends.csv', index=False)
#
#
# # TEST
# for col_num in range(1, len(df.columns)):
#     my_col = df.iloc[:, col_num]
#     max_value = max(my_col)
#     if max_value != 100:
#         print(max_value, my_col.name)
#     else:
#         pass