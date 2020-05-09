import pandas as pd
from data_clean_funs import covid_cases_data_clean as ccd

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

Confirmed.to_csv('data/confirmed.csv', index=False)
Death.to_csv('data/death.csv', index=False)
Recovered.to_csv('data/recovered.csv', index=False)