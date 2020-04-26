import pandas as pd
import numpy as np
from data_grip import covid_cases_data as ccd
import matplotlib.pyplot as plt
import altair as alt
import datetime as dt
alt.renderers.enable('html')

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


# boxOffice data processing, need better solution
boxOffice = pd.read_csv('data/boxOffice_20200420.csv')
boxOffice['date'] = pd.to_datetime(boxOffice['date'])
BoxOffice = boxOffice.drop(columns=['date.1']).set_index('date')
BoxOffice.index.name = 'index'

# dt.datetime.strptime('2020-04-20', '%Y-%m-%d').date()


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


Confirmed2 = transpose_for_altair(Confirmed, 'Confirmed')
Death2 = transpose_for_altair(Death, 'Death')
Recovered2 = transpose_for_altair(Recovered, 'Recovered')
BoxOffice2 = transpose_for_altair(BoxOffice, 'BoxOffice')


def easy_merge(df_a, df_b):
    my_index = ['Country', 'Day']
    new_df = pd.merge(df_a, df_b, how='left', left_on=my_index, right_on=my_index)
    return new_df


Covid = easy_merge(Confirmed2, Death2)
Covid = easy_merge(Covid, Recovered2)
Covid = easy_merge(Covid, BoxOffice2)


"""
altair viz: covid vs BoxOffice
"""

# source = Covid.loc[Covid['Country'] == 'KR']
source = Covid

chart = alt.Chart(source).mark_circle(size=60).encode(
    x=alt.X(
        'Confirmed', scale=alt.Scale(domain=[0, 15000])
    ),
    y=alt.Y(
        'BoxOffice', scale=alt.Scale(domain=[0, 30000000])
    ),
    color='Country',
    tooltip=['Country', 'Day', 'Confirmed', 'Death', 'Recovered', 'BoxOffice']
).properties(
    width=960,
    height=720
)
# ).transform_filter(
    # alt.FieldOneOfPredicate(field='Country', oneOf=['KR', 'TW', 'CN', 'IT'])
    # # alt.FieldRangePredicate(field='Confirmed', range=[100, 50000])
# )


chart.save('temp/viz/test4.html')


""" 
TO BE UPDATE
add population to compare
use sq rt to revalue the data, in order to make the viz more visible
"""