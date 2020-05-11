import pandas as pd
import numpy as np
import geopandas as gpd
import json
import altair as alt
from altair_viz import map_reader as mapr
alt.renderers.enable('html')

# load text data
today_data = pd.read_csv('data/covid_today.csv')

all_data = pd.read_csv('data/all_data.csv')
# load geo data
# call gis data reading functions from map_reader
# which reads shapefile with geopandas
base_map_path = 'data/base_map/base_map_4326.shp'
gdf = mapr.get_gpd_df(base_map_path, True)

"""
main map
"""
# merge geo data with covid_today data
country_map = gdf.merge(today_data, left_on='ct_code', right_on='country_code', how='outer')
# covert geo data frame to json and extract 'feature' section
choro_json = json.loads(country_map.to_json())
choro_data = alt.Data(values=choro_json['features'])


def gen_map(geo_data, color_column, tooltip, scale_type, color_scheme='bluegreen'):
    """
    Generates Toronto neighbourhoods map with building count choropleth
    :return:
    """

    # Add Base Layer
    base = alt.Chart(geo_data).mark_geoshape(
        color='#EFEFEF',  # color for countries with no data
        stroke='white',
        strokeWidth=0.5
    ).encode(
    ).properties(
        width=800,
        height=800
    )
    # Add choropleth Layer
    choro = alt.Chart(geo_data).mark_geoshape(
        stroke='white',
        strokeWidth=0.5,
        opacity=0.8
    ).encode(
        alt.Color(color_column,
                  type='quantitative',
                  scale=alt.Scale(type=scale_type,
                                  scheme=color_scheme),
                  title="Active Cases",
                  legend=alt.Legend(orient="bottom")
                  ),
        tooltip=tooltip
    )
    return base + choro


map_1 = gen_map(geo_data=choro_data,
                color_column='properties.active',
                tooltip=['properties.formal_nam:N',
                         'properties.active:Q',
                         'properties.confirmed:Q',
                         'properties.death:Q',
                         'properties.recovered:Q'],
                scale_type='symlog',
                # ['linear', 'log', 'pow', 'sqrt', *'symlog', 'identity',
                # 'sequential', 'time', 'utc', 'quantile', 'quantize',
                # 'threshold', 'bin-ordinal', 'ordinal', 'point', 'band']
                color_scheme='yelloworangered')
map_1.save('temp/viz/test_map.html')

"""
confirmed sqrt vs search_trend
"""
# for i in all_data.columns:
#     print(i)
# # country_code
# # date
# # confirmed
# # death
# # recovered
# # box_office_full
# # box_office_2019_mean
# # search_trend
# # box_office_norm
# # confirmed_sqrt
# # death_sqrt
# # recovered_sqrt
# # active_cases
# # active_cases_sqrt
# # country_name


def gen_sqrt_vs_st(source=all_data):
    base = alt.Chart(source).mark_point(size=60).encode(
        x='confirmed_sqrt',
        y='search_trend',
        color='country_code',
        tooltip=['country_name', 'date', 'confirmed', 'death', 'recovered', 'search_trend']
    )

    chart = base.properties(
        title="Search Trend vs Confirmed Cases",
        width=960,
        height=720
    )

    # get unique country_codes
    country_names = df['country_name'].unique().tolist()

    country_dropdown = alt.binding_select(options=country_names)
    country_select = alt.selection_single(fields=['country_name'], bind=country_dropdown, name="country_name")

    filtered = chart.add_selection(
        country_select
    ).transform_filter(
        country_select
    )

    return filtered


scatter_1 = gen_sqrt_vs_st()
scatter_1.save('temp/viz/test8_cf_vs_st.html')