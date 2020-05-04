import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from data_get import covid_cases_data_clean as ccd

import altair as alt
alt.renderers.enable('html')

"""
import data
"""

# import case data
path = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
file1 = "time_series_covid19_confirmed_global.csv"
file2 = "time_series_covid19_deaths_global.csv"
file3 = "time_series_covid19_recovered_global.csv"

confirmed = pd.read_csv(path + file1)
death = pd.read_csv(path + file2)
recovered = pd.read_csv(path + file3)

Confirmed = ccd.remodeling(df=confirmed, df_name='confirmed')
Death = ccd.remodeling(df=death, df_name='death')
Recovered = ccd.remodeling(df=recovered, df_name='recovered')

# # test
# plt.cla()
# Confirmed.loc[:, :].plot(legend=None)
# Death.loc[:, :].plot(legend=None)
# Recovered.loc[:, :].plot(legend=None)
# # test end


"""
to case by day 1
"""


def remove_zeros(my_array):
    """
    # remove leading zeros to avoid future errors
    # modified from mits's code at
    # https://www.geeksforgeeks.org/remove-leading-zeros-from-an-array/
    """
    # get length of the array
    n = len(my_array)
    # holder to store the
    # first non-zero number's index
    ind = -1
    # loop through the array
    # and find the first non-zero number
    for i in range(n):
        if my_array[i] != 0:
            ind = i
            break
    # if there's no non-zero number
    # make the array with only one NaN
    if ind == -1:
        #
        b = [np.nan]
    # else create an array to store
    # numbers apart from leading
    # zeros b[n - ind];
    else:
        b = [0] * (n - ind)
        # store the numbers
        # removing leading zeros
        for i in range(n - ind):
            b[i] = my_array[ind + i]
    return b


def add_na(my_list):
    """
    in a list of arrays,
    add nan to the end of each array
    to make them the equal length
    """
    # get the length of all arrays
    all_len = [len(i) for i in my_list]
    # get the max length
    max_len = max(all_len)
    # iterate through the list
    for i in my_list:
        # when array is not the longest one
        # add nan for t times
        # t = difference btwn max length and array length
        if len(i) < max_len:
            for t in range((max_len - len(i))):
                i.append(np.nan)
        else:
            pass
    return my_list


def by_day_converter(df):
    """
    convert covid data to day 1, day 2 ... day n format
    using the former two functions
    """
    # holders for indices (column names)
    # and covid case count lists
    indices = []
    counts = []
    for (col, cont) in df.iteritems():
        indices.append(col)
        counts.append(cont.values)
    # holder for count lists
    # after removing leading zeros
    new_counts = []
    for a in counts:
        new_counts.append(remove_zeros(a))
    # add na to the end of arrays
    new_counts = add_na(new_counts)
    # create a new df with these arrays and using the countries as column names
    new_df = pd.DataFrame(new_counts, index=indices).T
    # convert float numbers to integers
    # use 'Int64' instead of int to accept missing values
    new_df = new_df.astype('Int64')
    # add day number column
    new_df['Day'] = (new_df.index+1).astype(str)
    new_df['Day'] = new_df['Day'].str.zfill(3)
    new_df['Day'] = 'Day_' + new_df['Day']

    # new_df = new_df.set_index('Day')
    return new_df


# the following returned data frame without transposing

# Confirmed2 = by_day_converter(Confirmed)
# Death2 = by_day_converter(Death)
# Recovered2 = by_day_converter(Recovered)


def transpose_for_altair(df):
    df = by_day_converter(df)
    colNum = len(df.columns)
    rowNum = len(df)
    new_df = pd.DataFrame(columns=['Country', 'Count', 'Day'])
    for i in range(0, colNum-1):
        country = [df.columns[i]] * rowNum
        country = pd.Series(country)
        count = df.iloc[:, i].to_frame()
        days = df.iloc[:, colNum - 1]
        new_rows = pd.DataFrame(pd.concat([country, count, days], axis=1))
        new_rows.columns = ['Country', 'Count', 'Day']
        new_df = pd.concat([new_df, new_rows])
    return new_df


# test 2
source = transpose_for_altair(Confirmed)
highlight = alt.selection(type='single', on='mouseover',
                          fields=['Country'], nearest=True)
base = alt.Chart(source).mark_line().encode(
    y='Count',
    x='Day',
    color=alt.Color('Country', legend=None),
    tooltip=['Country', 'Day', 'Count']
)

points = base.mark_circle().encode(
    opacity=alt.value(0)
).add_selection(
    highlight
).properties(
    width=1024,
    height=720
)

lines = base.mark_line().encode(
    tooltip=['Country', 'Day', 'Count'],
    color=alt.condition(highlight, 'Country', alt.value('lightgray'), legend=None),
    size=alt.condition(highlight, alt.value(3), alt.value(1))
)

chart = points+lines
chart.save('temp/viz/test2.html')


# test 3
source = transpose_for_altair(Confirmed)
highlight = alt.selection_single(
    on='mouseover',
    fields=['Country'],
    nearest=False,
    empty='none'
)
chart = alt.Chart(source).mark_line().encode(
    y='Count',
    x='Day',
    size=alt.condition(highlight, alt.value(3), alt.value(1)),
    color=alt.condition(highlight, 'Country', alt.value('lightgray'), legend=None),
    tooltip=['Country', 'Count']
).properties(
    width=1024,
    height=720
).add_selection(
    highlight
)

chart.save('temp/viz/test3.html')


"""
Question: how to make the selected line on top
"""