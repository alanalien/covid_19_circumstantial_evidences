import pandas as pd
import numpy as np


def transpose_for_altair(df, df_name):
    # df = new_index_for_viz(df)
    col_num = len(df.columns)
    row_num = len(df)
    new_df = pd.DataFrame(columns=['country_code', df_name, 'date'])
    for i in range(1, col_num):
        country = [df.columns[i]] * row_num
        country = pd.Series(country)
        count = df.iloc[:, i].to_frame()
        days = df.iloc[:, 0]
        new_rows = pd.DataFrame(pd.concat([country, count, days], axis=1))
        new_rows.columns = ['country_code', df_name, 'date']
        new_df = pd.concat([new_df, new_rows])
    new_df['country_code'] = new_df['country_code'].str[:2]
    new_df = new_df.reset_index(drop=True)
    return new_df


def easy_merge(df_a, df_b):
    df_a['date'] = df_a['date'].astype(str)
    df_b['date'] = df_b['date'].astype(str)
    my_index = ['country_code', 'date']
    new_df = pd.merge(df_a, df_b, how='left', left_on=my_index, right_on=my_index)
    return new_df