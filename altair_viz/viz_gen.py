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
base_map_path = 'data/base_map/base_map_50m_4326.shp'
gdf = mapr.get_gpd_df(base_map_path, True)


color_list = ['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime',
              'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite',
              'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood',
              'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan',
              'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta',
              'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue',
              'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray',
              'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold',
              'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki',
              'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan',
              'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon',
              'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue',
              'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid',
              'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise',
              'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace',
              'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred',
              'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown',
              'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray',
              'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet',
              'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']

keys = ['active', 'confirmed', 'country_code', 'death', 'iso_a2', 'name_cn', 'name_en', 'recovered', 'reg', 'sub_reg']

"""
main map
"""
# merge geo data with covid_today data
country_map = gdf.merge(today_data, left_on='iso_a2', right_on='country_code', how='outer')
# covert geo data frame to json and extract 'feature' section
choro_json = json.loads(country_map.to_json())
choro_data = alt.Data(values=choro_json['features'])


def map_generator():
    """
    Generates Toronto neighbourhoods map with building count choropleth
    :return:
    """

    # Add Base Layer
    base = alt.Chart(choro_data).mark_geoshape(
        color='#EFEFEF',  # color for countries with no data
        stroke='white',
        strokeWidth=0.5
    ).encode(
    ).properties(
        width=750,
        height=750
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
                                    offset=-200)
                  )
    )

    # add selector layer
    selection = alt.selection_multi(fields=['properties.country_code'])
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

    out = base + choro + selector

    out = out.configure_view(
        strokeWidth=0
    )

    return out


main_map = map_generator()
main_map.save('temp/viz/test_map.html')


"""
confirmed sqrt vs search_trend
"""


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