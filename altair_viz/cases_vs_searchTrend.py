import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from data_grip import covid_cases_data as ccd
from data_grip import search_trend_data as std

import altair as alt
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