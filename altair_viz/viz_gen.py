import pandas as pd
import numpy as np
import geopandas as gpd
import json
import altair as alt
from altair_viz import map_reader as mapr

alt.data_transformers.disable_max_rows()  # disable 5000 rows limitation
alt.renderers.enable('html')

# load text data
today_data = pd.read_csv('data/covid_today.csv')

all_data = pd.read_csv('data/all_data.csv')
all_data['date'] = pd.to_datetime(all_data['date'])  # date to datetime format
all_data = all_data.dropna(subset=['country_code'])  # drop mistakenly generated NAs

# load geo data
# call gis data reading functions from map_reader
# which reads shapefile with geopandas
base_map_path = 'data/base_map/base_map_50m_4326.shp'
gdf = mapr.get_gpd_df(base_map_path, True)

# merge geo data with covid_today data
country_map = gdf.merge(today_data, left_on='iso_a2', right_on='country_code', how='outer')
# covert geo data frame to json and extract 'feature' section
choro_json = json.loads(country_map.to_json())
choro_data = alt.Data(values=choro_json['features'])

# rename country_code column to 'properties.country_code', to match with json
all_data.columns = ['properties.country_code', 'date', 'confirmed', 'death', 'recovered',
                    'box_office_full', 'search_trend', 'box_office_2019_mean',
                    'box_office_norm', 'active_cases', 'country_name',
                    'region', 'sub_region', 'country_name_cn']

# get a list for drop down
# country_code_list = all_data['properties.country_code'].unique().tolist()

# test = all_data.sort_values(by=['properties.country_code', 'date'])
# test['box_office_full'] = test['box_office_full'].fillna(method='ffill')


"""
main map
"""

# main selection
selection = alt.selection_multi(fields=['properties.country_code'], empty='all')
# empty:enum(‘all’, ‘none’)
# By default, all data values are considered to lie within an empty selection.
# When set to none, empty selections contain no data values

# Add Base Layer
base = alt.Chart(choro_data).mark_geoshape(
    color='#EFEFEF',  # color for countries with no data
    stroke='white',
    strokeWidth=0.5
).encode(
).properties(
    width=1000,
    height=700
)

# Add choropleth Layer
choro = alt.Chart(choro_data).mark_geoshape(
    stroke='white',
    strokeWidth=0.5,
    opacity=0.8
).encode(
    alt.Color('properties.active',
              type='quantitative',
              scale=alt.Scale(type='symlog',
                              # ['linear', 'log', 'pow', 'sqrt', *'symlog', 'identity',
                              # 'sequential', 'time', 'utc', 'quantile', 'quantize',
                              # 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band'],
                              scheme='yelloworangered'),
              title="Active Cases",
              legend=alt.Legend(orient="bottom",
                                offset=-150)
              )
)

# add selector layer
select_color = alt.condition(selection,
                             alt.value('black'),
                             alt.value('white')
                             )
select_opacity = alt.condition(selection,
                               if_true=alt.value(0.5),
                               if_false=alt.value(0)
                               )
selector = alt.Chart(choro_data).mark_geoshape(
    stroke='white',
    strokeWidth=0.5,
    opacity=0
).encode(
    color=select_color,
    opacity=select_opacity,
    tooltip=['properties.name_en:N',
             'properties.active:Q',
             'properties.confirmed:Q',
             'properties.death:Q',
             'properties.recovered:Q'
             ]
).add_selection(
    selection
)

main_map = base + choro + selector
# main_map.save('viz_file/test_map.html')


"""
####################################################################################################################
####################################################################################################################
#################################### I'M A VERY KIND AND OBVIOUS SEPARATOR #########################################
####################################################################################################################
####################################################################################################################
"""


"""
1/6 search trend by date
"""

st_line = alt.Chart(all_data).mark_line(
    color='blue',
    size=0.75
).encode(
    x=alt.X('date:T'),
    y=alt.Y('search_trend:Q'),
    color=alt.Color('country_name:N',
                    legend=None
                    ),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
).properties(
    title="Search Trend by Date",
    width=250,
    height=180
)

# st_line.save('temp/viz/st_L1.html')
st_L1 = st_line

"""
2/6 box office by date *box office data normalized by last year average
"""
bx_no_na = all_data.dropna(subset=['box_office_full'])

bx_line = alt.Chart(bx_no_na).mark_line(
    color='blue',
    size=0.75
).encode(
    x='date:T',
    y='box_office_norm:Q',
    color=alt.Color('country_name:N',
                    legend=None
                    ),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
).properties(
    title="Box Office by Date",
    width=250,
    height=180
).transform_impute(
    impute='date:T',
    key='box_office_full:Q'
)

# bx_line.save('viz_file/bx_L2.html')
bx_L2 = bx_line

"""
3/6 COVID case data: confirmed, death, recovered
"""

# confirmed
cf_line = alt.Chart(all_data).mark_line(
    color='blue',
    size=0.75
).encode(
    x='date:T',
    y=alt.Y('confirmed:Q', scale=alt.Scale(zero=True, type='sqrt')),
    color=alt.Color('country_name:N',
                    legend=None
                    ),
    tooltip=['country_name', 'date', 'confirmed']
).properties(
    title="COVID-19 Cases by Date",
    width=250,
    height=180
)

# death
dt_line = alt.Chart(all_data).mark_line(
    color='red',
    size=0.75
).encode(
    x='date:T',
    y=alt.Y('death:Q', scale=alt.Scale(zero=True, type='sqrt')),
    color=alt.Color('country_name:N',
                    legend=None
                    ),
    tooltip=['country_name', 'date', 'death']
)

# recoverd
rc_line = alt.Chart(all_data).mark_line(
    color='green',
    size=0.75
).encode(
    x='date:T',
    y=alt.Y('recovered:Q', scale=alt.Scale(zero=True, type='sqrt')),
    color=alt.Color('country_name:N',
                    legend=None
                    ),
    tooltip=['country_name', 'date', 'recovered']
)

covid_line = cf_line + dt_line + rc_line
# covid_line.save('viz_file/covid_L3.html')
covid_L3 = covid_line


"""
4/6 confirmed vs search_trend
"""
# drop confirmed = 0 to avoid skew
cf_drop_zero = all_data.loc[all_data['confirmed'] != 0, :].reset_index(drop=True)

st_scatter = alt.Chart(cf_drop_zero).mark_circle(size=15).encode(
    x=alt.X('confirmed:Q', scale=alt.Scale(zero=False, type='sqrt')),
    y=alt.Y('search_trend:Q', scale=alt.Scale(zero=True, type='linear')),
    color=alt.Color('country_name:N',
                    # 'region:N'
                    # legend=None
                    ),
    opacity=alt.value(0.3),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
).properties(
    title="Search Trend vs Confirmed Cases",
    width=250,
    height=180
)

# st_scatter.save('viz_file/st_R1.html')
st_R1 = st_scatter


"""
5/6 confirmed cases vs box office (normalized by last year's average) heat map
"""

cf_drop_zero = all_data.loc[all_data['confirmed'] != 0, :].reset_index(drop=True)  # drop zeros

bx_scatter = alt.Chart(cf_drop_zero).mark_circle(size=15).encode(
    x=alt.X('confirmed:Q', scale=alt.Scale(zero=False, type='sqrt')),
    y=alt.Y('box_office_norm:Q', scale=alt.Scale(zero=True, type='linear')),
    color=alt.Color('country_name:N',
                    # legend=None
                    ),
    opacity=alt.value(0.8),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
).properties(
    title="Box Office vs Confirmed Cases",
    width=250,
    height=180
)

# bx_scatter.save('viz_file/bx_R2.html')
bx_R2 = bx_scatter


"""
6/6 active cases by date
"""

act_area = alt.Chart(all_data).mark_area().encode(
    x="date:T",
    y="active_cases:Q",
    color=alt.Color("country_name:N", legend=None),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'active_cases']
).properties(
    title="Active Cases by Date",
    width=1600,
    height=180
)

# act_area.save('viz_file/act_B1.html')
act_B1 = act_area


"""
FINALLY
CONCAT
"""

# main_map
st_L1 = st_L1.transform_filter(selection)
bx_L2 = bx_L2.transform_filter(selection)
covid_L3 = covid_L3.transform_filter(selection)
st_R1 = st_R1.transform_filter(selection)
bx_R2 = bx_R2.transform_filter(selection)
act_B1 = act_B1.transform_filter(selection)

output = (((st_L1 & bx_L2 & covid_L3) | main_map | (st_R1 & bx_R2)) & act_B1).configure_axis(
    grid=False,
    labelBound=True,

).configure_view(
    strokeOpacity=0
)
output.save('index.html')





"""
####################################################################################################################
####################################################################################################################
################################################### THE END ########################################################
####################################################################################################################
####################################################################################################################
"""

# """
# confirmed vs search_trend
# """
#
# st_scatter = alt.Chart(all_data).mark_circle(size=15).encode(
#     x=alt.X('confirmed:Q', scale=alt.Scale(zero=False, type='sqrt')),
#     y=alt.Y('search_trend:Q', scale=alt.Scale(zero=True, type='linear')),
#     color=alt.Color('region:N'),
#     opacity=alt.value(0.3),
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
# ).properties(
#     title="Search Trend vs Confirmed Cases",
#     width=600,
#     height=170
# )
#
# st_scatter.save('temp/viz/test8_cf_vs_st.html')
#
# """
# confirmed vs search trend heat map
# """
#
# cf_drop_zero = all_data.loc[all_data['confirmed'] != 0, :].reset_index(drop=True)  # drop zeros
#
# st_heat_map = alt.Chart(cf_drop_zero).mark_rect().encode(
#     x=alt.X('confirmed:Q', scale=alt.Scale(zero=False, type='log')),
#     # ['linear', 'log', 'pow', 'sqrt', *'symlog', 'identity',
#     # 'sequential', 'time', 'utc', 'quantile', 'quantize',
#     # 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band'],
#     y=alt.Y('search_trend:Q', scale=alt.Scale(zero=True, type='linear')),
#     color=alt.Color('count()', scale=alt.Scale(scheme='yelloworangered'))
# )
# points = alt.Chart(cf_drop_zero).mark_circle(
#     color='black',
#     size=5,
# ).encode(
#     x='confirmed_sqrt:Q',
#     y='box_office_norm:Q',
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
# )
#
# st_heat_map = st_heat_map + points
#
# st_heat_map.save('temp/viz/test13_st_heat_map.html')
#
#
# """
# search trend by time
# """
#
# st_line = alt.Chart(all_data).mark_line(
# ).encode(
#     x='date:T',
#     y='search_trend:Q',
#     color='blue'
#     # tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
# ).properties(
#     title="Search Trend by Date",
#     width=600,
#     height=170
# )
# cf_line = alt.Chart(all_data).mark_line(
#     color='red'
# ).encode(
#     x='date:T',
#     y='confirmed:Q',
#     color=alt.Color('country_name:N',
#                     # scale=alt.Scale(scheme='yelloworangered'),
#                     legend=None
#                     )
#     # tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
# ).properties(
#     title="Search Trend by Date",
#     width=600,
#     height=170
# )
#
# st_line.save('temp/viz/test10_st.html')
# cf_line.save('temp/viz/test15_cf.html')
#
#
# """
# confirmed cases vs box office (normalized by last year's average) heat map
# """
# act_drop_zero = all_data.loc[all_data['active_cases'] > 10, :].reset_index(drop=True)  # drop zeros
#
# bx_heat_map = alt.Chart(act_drop_zero).mark_rect().encode(
#     x=alt.X('active_cases:Q', bin=True, type='quantitative'),
#     y=alt.Y('box_office_norm:Q', bin=True),
#     color=alt.Color('count()', scale=alt.Scale(scheme='yelloworangered'))
# )
# points = alt.Chart(act_drop_zero).mark_circle(
#     color='black',
#     size=5,
# ).encode(
#     x=alt.X('active_cases:Q', type='quantitative'),
#     y=alt.Y('box_office_norm:Q'),
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'active_cases' 'box_office_full']
# )
#
# cf_vs_bx = bx_heat_map + points
# cf_vs_bx.save('temp/viz/test9_cf_vs_bx.html')
#
# """
# confirmed cases vs box office (normalized by last year's average
# """
#
# cf_drop_zero = all_data.loc[all_data['confirmed'] != 0, :].reset_index(drop=True)  # drop zeros
#
# bx_scatter = alt.Chart(cf_drop_zero).mark_circle(size=15).encode(
#     x='confirmed_4rt',
#     y='box_office_norm',
#     color=alt.Color('country_name:N',
#                     legend=None
#                     ),
#     opacity=alt.value(0.3),
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
# ).properties(
#     title="Box Office vs Confirmed Cases",
#     width=400,
#     height=170
# )
#
# cf_vs_bx.save('temp/viz/test9_cf_vs_bx.html')
#
# """
# search trend by time
# """
# st_line = alt.Chart(all_data).mark_line(
# ).encode(
#     x='date',
#     y='box_office_norm:Q',
#     color=alt.Color('region:N', scale=alt.Scale(range=color_range)),
# ).properties(
#     title="Box Office by Date",
#     width=350,
#     height=180
# )
#
# st_line.save('temp/viz/test11_bx.html')
#
# """
# case line chart
# """
#
# act_area = alt.Chart(all_data).mark_area().encode(
#     x="date:T",
#     y="active_cases:Q",
#     color=alt.Color("country_name:N", legend=None),
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'active_cases']
# ).properties(
#     title="Active Cases by Date",
#     width=1600,
#     height=170
# )
#
# act_area.save('temp/viz/test12_act_area.html')
#
#
# """
# concat
# """
#
# # vertical_charts = alt.vconcat(cf_vs_st, st_line, cf_vs_bx)
# # upper = alt.hconcat(vertical_charts, main_map)
# # output = alt.vconcat(upper, act_area).configure_view(strokeOpacity=0)
# # sqrt_vs_st | main_map
#
# # output.save('temp/viz/test9_compound.html')
#
# # ((chart1 & chart2 & chart3) | map) & (bigchart)
#
# (main_map & st_line).save('temp/viz/test9_compound.html')