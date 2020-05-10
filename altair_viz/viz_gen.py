import pandas as pd
import numpy as np
import geopandas as gpd
import json
import altair as alt
from altair_viz import map_reader as mapr
alt.renderers.enable('html')

df = pd.read_csv('data/all_data.csv')

for i in df.columns:
    print(i)
# country_code
# date
# confirmed
# death
# recovered
# box_office_full
# box_office_2019_mean
# search_trend
# box_office_norm
# confirmed_sqrt
# death_sqrt
# recovered_sqrt
# active_cases
# active_cases_sqrt
# country_name


"""
main map
"""
base_map_path = 'data/base_map/base_map_3395.shp'
gdf = mapr.get_gpd_df(base_map_path, True)

country_map = gdf.merge(df, left_on='ct_code', right_on='country_code', how='left')


"""
confirmed sqrt vs search_trend
"""
source = df
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

filtered.save('temp/viz/test8_cf_vs_st.html')