import pandas as pd
import numpy as np
import geopandas as gpd
import json
import altair as alt
from altair_viz import map_reader as mapr
alt.renderers.enable('html')

# all_data['search_trend'].unique()
# load text data
today_data = pd.read_csv('data/covid_today.csv')

all_data = pd.read_csv('data/all_data.csv')
all_data['date'] = pd.to_datetime(all_data['date'])
all_data = all_data.dropna(subset=['country_code'])
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
# 'active', 'confirmed', 'country_code', 'death', 'iso_a2', 'name_cn', 'name_en', 'recovered', 'reg', 'sub_reg'
all_data.columns = ['properties.country_code', 'date', 'confirmed', 'death', 'recovered',
                    'box_office_full', 'search_trend', 'box_office_2019_mean',
                    'box_office_norm', 'confirmed_sqrt', 'confirmed_4rt', 'death_sqrt',
                    'recovered_sqrt', 'active_cases', 'active_cases_sqrt', 'country_name',
                    'region', 'sub_region', 'country_name_cn']
country_code_list = all_data['properties.country_code'].unique().tolist()

# test = all_data.sort_values(by=['properties.country_code', 'date'])
# test['box_office_full'] = test['box_office_full'].fillna(method='ffill')


# main selection
selection = alt.selection_multi(fields=['properties.country_code'])

"""
main map
"""

# Add Base Layer
base = alt.Chart(choro_data).mark_geoshape(
    color='#EFEFEF',  # color for countries with no data
    stroke='white',
    strokeWidth=0.5
).encode(
).properties(
    width=1000,
    height=720
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
# main_map.save('temp/viz/test_map.html')


"""
confirmed sqrt vs search_trend
"""

color_range = ['#15C885', '#025EE0', '#fA8B2F', '#55D5FF', '#F5E150']
# null, africa, america, asia, euro, oceania


scatter_1_base = alt.Chart(all_data).mark_circle(size=15).encode(
    x='confirmed_sqrt',
    y='search_trend',
    color=alt.Color('region:N', scale=alt.Scale(range=color_range)),
    opacity=alt.value(0.3),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
).properties(
    title="Search Trend vs Confirmed Cases",
    width=600,
    height=190
)

# country_select = alt.selection_single(fields=['properties.country_name'], bind=selection, name="country_name")
cf_vs_st = scatter_1_base.add_selection(
    selection
)

cf_vs_st.save('temp/viz/test8_cf_vs_st.html')

"""
search trend by time
"""
st_line = alt.Chart(all_data).mark_line(
).encode(
    x='date',
    y='search_trend:Q',
    color=alt.Color('region:N', scale=alt.Scale(range=color_range)),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
).properties(
    title="Search Trend by Date",
    width=600,
    height=170
)

st_line.save('temp/viz/test10_st.html')


"""
confirmed cases vs box office (normalized by last year's average
"""
#
# heatmap = alt.Chart(all_data).mark_rect().encode(
#     alt.X('confirmed_4rt:Q', bin=True),
#     alt.Y('box_office_norm:Q', bin=True),
#     alt.Color('count()', scale=alt.Scale(scheme='yelloworangered'))
# )
# points = alt.Chart(all_data).mark_circle(
#     color='black',
#     size=5,
# ).encode(
#     x='confirmed_sqrt:Q',
#     y='box_office_norm:Q',
#     tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
# )
#
# cf_vs_bx = heatmap + points
# cf_vs_bx.save('temp/viz/test9_cf_vs_bx.html')


cf_vs_bx = alt.Chart(all_data).mark_circle(size=15).encode(
    x='confirmed_4rt',
    y='box_office_norm',
    color=alt.Color('region:N', scale=alt.Scale(range=color_range)),
    opacity=alt.value(0.3),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'box_office_full']
).properties(
    title="Box Office vs Confirmed Cases",
    width=600,
    height=170
)

cf_vs_bx.save('temp/viz/test9_cf_vs_bx.html')

"""
search trend by time
"""
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
# bx_line.save('temp/viz/test11_bx.html')

"""
case line chart
"""

act_area = alt.Chart(all_data).mark_area().encode(
    x="date:T",
    y="active_cases:Q",
    color=alt.Color("country_name:N", legend=None),
    tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'active_cases']
).properties(
    title="Active Cases by Date",
    width=1600,
    height=170
)

act_area.save('temp/viz/test12_act_area.html')


"""
concat
"""

vertical_charts = alt.vconcat(cf_vs_st, st_line, cf_vs_bx)
upper = alt.hconcat(vertical_charts, main_map)
output = alt.vconcat(upper, act_area).configure_view(strokeOpacity=0)
# sqrt_vs_st | main_map
output.save('temp/viz/test9_compound.html')