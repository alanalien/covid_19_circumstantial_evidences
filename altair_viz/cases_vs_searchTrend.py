import pandas as pd
from data_clean_funs import covid_cases_data_clean as ccd, table_merge_stack as tms
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

search_trend = pd.read_csv('data/search_trends_20200424.csv')
search_trend['date'] = pd.to_datetime(search_trend['date'])
search_trend = search_trend.set_index('date')


Confirmed2 = tms.transpose_for_altair(Confirmed, 'Confirmed')
Death2 = tms.transpose_for_altair(Death, 'Death')
Recovered2 = tms.transpose_for_altair(Recovered, 'Recovered')
SearchTrend2 = tms.transpose_for_altair(search_trend, 'SearchTrend')

Covid = tms.easy_merge(Confirmed2, Death2)
Covid = tms.easy_merge(Covid, Recovered2)
Covid = tms.easy_merge(Covid, SearchTrend2)

Covid['SearchTrend'] = Covid['SearchTrend'].astype(float)

country_table = pd.read_csv('data/country_table.csv')


"""
altair viz:
scatter plot for search trend vs case
"""
source = Covid

base = alt.Chart(source).mark_point(size=60).encode(
    x='Confirmed',
    y='SearchTrend',
    color='Country',
    tooltip=['Country', 'Day', 'Confirmed', 'Death', 'Recovered', 'SearchTrend']
).transform_calculate(
    # Generate Gaussian jitter with a Box-Muller transform
    jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
)


chart = base.properties(
    width=960,
    height=720
)


country_code = country_table['Code'].to_list()

country_dropdown = alt.binding_select(options=country_code)
country_select = alt.selection_single(fields=['Country'], bind=country_dropdown, name="Country")

filtered = base.add_selection(
    country_select
).transform_filter(
    country_select
).properties(title="Search Trend vs Confirmed Cases",
             width=960,
             height=720
             )


chart.save('temp/viz/test5.html')
filtered.save('temp/viz/test6.html')


# line chart
base2 = alt.Chart(source).mark_line().encode(
    x='Day',
    y='SearchTrend',
    color='Country',
    tooltip=['Country', 'Day', 'Confirmed', 'Death', 'Recovered', 'SearchTrend']
).properties(
    width=1280,
    height=960
)

base2.save('temp/viz/test7.html')