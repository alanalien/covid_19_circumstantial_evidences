import pandas as pd
import numpy as np


def new_index_for_viz(df):
    df.index.name = 'Date'
    df = df.reset_index()
    return df
# test = new_index_for_viz(Confirmed)


def transpose_for_altair(df, df_name):
    df = new_index_for_viz(df)
    colNum = len(df.columns)
    rowNum = len(df)
    new_df = pd.DataFrame(columns=['Country', df_name, 'Day'])
    for i in range(1, colNum-2):
        country = [df.columns[i]] * rowNum
        country = pd.Series(country)
        count = df.iloc[:, i].to_frame()
        days = df.iloc[:, 0]
        new_rows = pd.DataFrame(pd.concat([country, count, days], axis=1))
        new_rows.columns = ['Country', df_name, 'Day']
        new_df = pd.concat([new_df, new_rows])
    new_df['Country'] = new_df['Country'].str[:2]
    new_df = new_df.reset_index(drop=True)
    return new_df


def easy_merge(df_a, df_b):
    my_index = ['Country', 'Day']
    new_df = pd.merge(df_a, df_b, how='left', left_on=my_index, right_on=my_index)
    return new_df