import pandas as pd
import numpy as np
import time
import geopandas as gpd
import json
import altair as alt

import sys
# temporarily append the project directory to sys.path
# to allow the usage of the following modules
sys.path.append('/Users/wildgoose/PycharmProjects/covid_19_CE')

from altair_viz import map_reader as mapr

alt.data_transformers.disable_max_rows()  # disable 5000 rows limitation
alt.renderers.enable('html')

# load text data
today_data = pd.read_csv('data/covid_today.csv', keep_default_na=False)

all_data = pd.read_csv('data/all_data.csv')
all_data['date'] = pd.to_datetime(all_data['date'])  # date to datetime format

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
selection = alt.selection_multi(fields=['properties.country_code'], empty='none')
# empty:enum(‘all’, ‘none’)
# By default, all data values are considered to lie within an empty selection.
# When set to none, empty selections contain no data values

# Add Base Layer
base = alt.Chart(choro_data).mark_geoshape(
    color='#555555',  # color for countries with no data
    stroke='black',
    strokeWidth=0.5,
).encode(
).properties(
    width=1100,
    height=500,
).project('naturalEarth1')
# ['albers', 'albersUsa', 'azimuthalEqualArea', 'azimuthalEquidistant',
#  'conicConformal', 'conicEqualArea', 'conicEquidistant', 'equalEarth',
#  'equirectangular', 'gnomonic', 'identity', 'mercator', 'naturalEarth1',
#  'orthographic', 'stereographic', 'transverseMercator']

# Add choropleth Layer
choro = alt.Chart(choro_data).mark_geoshape(
    color='white',
    stroke='black',
    strokeWidth=0.5,
    opacity=0.8,
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
                                gradientLength=150,
                                offset=-150,
                                legendX=1000)
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
).encode(
    color=select_color,
    opacity=select_opacity,
    tooltip=[alt.Tooltip('properties.name_en:N', title='country_name'),  # title argument renames columns in tooltips
             alt.Tooltip('properties.active:Q', title='active'),
             alt.Tooltip('properties.confirmed:Q', title='confirmed'),
             alt.Tooltip('properties.death:Q', title='death'),
             alt.Tooltip('properties.recovered:Q', title='recovered')
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


def line_base_layer(column, chart_title, data=all_data, drop_na=False, w=300, h=250, number_format=0):
    """
    this function generates a basic line chart for further operations,
    with X axis as date and Y axis with deignated column that holds other data.
    specific for covid_CE project;

    :param column: string; Y axis column, must meet one of the column names in table
    :param chart_title: string; chart title, suggest to be the explaination of Y column data
    :param data: a pandas data frame, default all_data; the data table being used
    :param drop_na: boolean; in some cases the table needs to be manipulated, i.e. drop NA values
    :param w: width of the chart;
    :param h: height of the chart;
    :param number_format: altair uses D3 number formats
        0: alt.Axis(format='f'), original number, i.e. 1500000
        1: alt.Axis(format='~s'), decimal notation, i.e. 1.5M
        other formats can be found on: https://github.com/d3/d3-format#locale_format
        see also: https://github.com/altair-viz/altair/issues/1745

        note: '$.2f' is like $15.00, might be useful in tooltip optimization

    :return: an altair chart without top level configuration
    """

    # if drop_na is True then drop NA rows from the designated column
    if drop_na is True:
        data = data.dropna(subset=[column])
    else:
        data = data

    # see above... define the number format to show
    if number_format == 1:
        my_format = '~s'
    else:
        my_format = 'f'

    # basic tooltip infos
    my_tooltip = ['country_name', 'date', 'active_cases', 'confirmed', 'death', 'recovered']
    # append the designated column to the list
    my_tooltip.append(column)

    # create basic line chart, date is X and the designated column is Y
    base = alt.Chart(data).mark_line().encode(
        size=alt.value(1),
        y=alt.Y(column + ':Q', title='', axis=alt.Axis(format=my_format)),
        x=alt.X('date:T', title=''),
        color=alt.Color('country_name',
                        # legend=None
                        ),
        tooltip=my_tooltip
    ).properties(
        title=chart_title.upper(),
        width=w,
        height=h
    )

    return base


def multi_layer_interaction(column, chart_title, data=all_data, drop_na=False, w=300, h=220, number_format=0):
    """
    call the line_base_layer function to generate a chart and make it interactive,
    by adding multiple layers

    :params all params inherited from the line_base_layer function

    :return: an interactive altair chart without top level configuration
    """

    # call line_base_layer function to create base chart
    base = line_base_layer(column, chart_title, data, drop_na, w, h, number_format)

    # create a selector
    ruler = alt.selection(type='single', on='mouseover',
                          fields=['country_name', 'date'], nearest=True, empty='none')

    # add a point layer for better hover-on performance
    points = base.mark_circle().encode(
        color=alt.value('white'),
        size=alt.value(20),
        x='date:T',
        opacity=alt.condition(ruler, alt.value(1), alt.value(0))
    ).add_selection(
        ruler
    )

    # # add a line layer to highlight the lines  -- comment out due to not working
    # lines = base.mark_line().encode(
    #     # color condition is not defined (if_false='silver') to maintain color info when not selected
    #   size=alt.condition(ruler, alt.value(1.5), alt.value(1)),
    # )

    #

    # add a ruler layer to generate silver verticle lines when hover-on
    rules = alt.Chart(all_data).mark_rule(color='silver').encode(
        x='date:T'
    ).transform_filter(
        ruler
    )

    # new_chart = lines + points + rules
    new_chart = base + points + rules

    return new_chart


def concat_charts(w=300, h=220):
    """
    concatenated multiple charts by column names,
    defined by col_list the first line below

    :return: a horizontally concatenated chart
    """
    # define the column list
    col_list = ['confirmed', 'death', 'recovered']

    # create a first chart 'k'
    k = multi_layer_interaction(col_list[0], col_list[0].upper(), w=w, h=h, number_format=1)
    # concatenate the following charts 'j' to 'k'
    for i in col_list[1:]:
        j = multi_layer_interaction(i, i, w=w, h=h, number_format=1)
        k = k | j

    return k


def scatter_base_layer(column, chart_title, data=all_data, to_compare='confirmed',
                       add_info_col=False,
                       w=300, h=220, legend=False):
    """
    this function generates a scatter plot with highlighting performance,
    with X axis as a COVID fact (active/confirmed/...etc.) and Y axis with designated side fact column to compare with
    specific for covid_CE project;

    :param column: string; Y axis column, must meet one of the column names in table
    :param chart_title: string; chart title, suggest to be the explaination of Y column data
    :param data: a pandas data frame, default all_data; the data table being used
    :param to_compare: X axis column, a COVID fact to compare with circumstantial evidence, default 'confirmed'
    :param add_info_col: default false, determine whether to add an additional column to tooltip
    :param w: width of the chart;
    :param h: height of the chart;
    :param legend: whether to keep a legend; since the final result is a compound chart, only one legend is needed

    :return: an interactive altair scatter plot without top level configuration
    """

    # drop zeroes in the compare column to avoid skewing
    # to_compare: the comparing column
    data_drop_zero = data.loc[all_data[to_compare] != 0, :].reset_index(drop=True)

    # create a hover-on selector
    highlight = alt.selection(type='single', on='mouseover',
                              fields=['country_name', 'date'], nearest=True, empty='none')

    # basic tooltip infos
    my_tooltip = ['country_name', 'date', 'active_cases', 'confirmed', 'death', 'recovered']

    # append the designated column to the list
    # when there's demands to add additional column, i.e. add_info_col=True, then add it as well
    if add_info_col is True:
        my_tooltip.append('box_office_full')
    else:
        pass
    my_tooltip.append(column)

    # whether to keep the plot legend
    if legend is True:
        color_settings = alt.condition(highlight, alt.value('white'),
                                       alt.Color('country_name' + ':N',
                                                 title='Country Name'
                                                 )
                                       )
    else:
        color_settings = alt.condition(highlight, alt.value('white'),
                                       alt.Color('country_name' + ':N',
                                                 # legend=None
                                                 )
                                       )

    chart = alt.Chart(data_drop_zero).mark_circle(size=15).encode(
        x=alt.X(to_compare + ':Q', scale=alt.Scale(zero=False, type='symlog'), axis=alt.Axis(labels=False)),
        y=alt.Y(column + ':Q', scale=alt.Scale(zero=True, type='linear'), axis=alt.Axis(labels=False)),
        color=color_settings,
        size=alt.condition(highlight, alt.value(30), alt.value(15)),
        #         size=alt.Size('box_office_norm', legend=None),
        opacity=alt.condition(highlight, alt.value(1), alt.value(0.3)),
        tooltip=my_tooltip
    ).properties(
        title=chart_title.upper(),
        width=w,
        height=h
    ).add_selection(
        highlight
    )
    return chart


def area_base_layer(column='active_cases', chart_title='Active Cases by Date',
                    data=all_data, w=800, h=220):
    """
    this function generates an area chart that shows accumulated active cases of the selected countries

    :param column: string; Y axis column, must meet one of the column names in table
    :param chart_title: string; chart title, suggest to be the explaination of Y column data
    :param data: a pandas data frame, default all_data; the data table being used
    :param w: width of the chart;
    :param h: height of the chart;

    :return: an altair area chart
    """
    ruler = alt.selection(type='single', on='mouseover',
                          fields=['country_name', 'date'], nearest=True, empty='none')

    my_tooltip = ['country_name', 'date', 'active_cases', 'confirmed', 'death', 'recovered']
    # my_tooltip.append(column)

    areas = alt.Chart(data).mark_area().encode(
        x=alt.X("date:T", title=''),
        y=alt.Y(column + ':Q', title='', scale=alt.Scale(zero=False, type='sqrt'), axis=alt.Axis(format='~s')),
        color=alt.Color("country_name:N",
                        # legend=None
                        ),
    ).properties(
        title=chart_title.upper(),
        width=w,
        height=h
    )

    bars = areas.mark_bar().encode(
        x="date:T",
        y=alt.Y(column + ':Q', scale=alt.Scale(zero=False, type='sqrt')),
        color=alt.Color("country_name:N",
                        legend=None
                        ),
        opacity=alt.value(0),
        tooltip=my_tooltip
    ).add_selection(
        ruler
    )

    rules = alt.Chart(all_data).mark_rule(color='silver').encode(
        x='date:T',
    ).transform_filter(
        ruler
    )

    chart = areas + bars + rules

    return chart


def chart_configures(my_chart):
    """
    altair top-level configurations
    :param my_chart: the chart/compound charts to configure

    :return: configured altair chart
    """
    configured_chart = my_chart.configure(
        background='#111111',
        # padding=50,
        padding={"left": 50, "top": 50, "right": 100, "bottom": 50}
    ).configure_mark(
        cursor='crosshair'
    ).configure_view(
        strokeOpacity=0,
        # fill='#555555',
        cornerRadius=5
    ).configure_axis(
        # axis ticks configure
        tickOpacity=0,
        # axis name text configure
        titleFontSize=12,
        titleColor='white',
        titleFont='Helvetica',
        titleFontWeight=900,
        titleAnchor='end',
        titlePadding=12,
        # axis (main) configure
        domainColor='white',
        domainWidth=3,
        # grid configure
        # grid=False,
        gridColor='#AAAAAA',
        gridOpacity=0.5,
        # axis lable number configure
        labelBound=True,
        labelFont='Helvetica',
        labelFontWeight='lighter',
        labelFontSize=10,
        labelColor='#AAAAAA',
        # ticks configure
    ).configure_title(
        color='white',
        fontSize=15,
        font='Helvetica',
        fontStyle='italic',
        anchor='end',
        offset=10
    ).configure_legend(
        columnPadding=20,
        labelColor='white',
        labelFont='Helvetica',
        labelLimit=80,
        symbolLimit=10,
        symbolOffset=10,
        titleColor='white',
        titleFont='Helvetica'

    )
    return configured_chart


# driver codes

st_L1 = multi_layer_interaction('search_trend', 'Search Trend Index')
bx_L2 = multi_layer_interaction('box_office_norm', 'Normalized Box Office Index', drop_na=True)
covid_C1 = concat_charts(w=300, h=220)
st_S1 = scatter_base_layer('search_trend', 'search trend vs confirmed cases', legend=True)
bx_S2 = scatter_base_layer('box_office_norm', 'box office vs confirmed cases', add_info_col=False, legend=True)
covid_A1 = area_base_layer()

st_L1 = st_L1.transform_filter(selection)
bx_L2 = bx_L2.transform_filter(selection)
covid_C1 = covid_C1.transform_filter(selection)
st_S1 = st_S1.transform_filter(selection)
bx_S2 = bx_S2.transform_filter(selection)
covid_A1 = covid_A1.transform_filter(selection)

# output = (((st_L1 & bx_L2 & covid_L3) | main_map | (st_R1 & bx_R2)) & act_B1)

output = (((st_L1 | st_S1) & (bx_L2 | bx_S2)) | main_map) & (covid_C1 | covid_A1)

output = chart_configures(output)

output.save('altair_viz/new_viz.html',
            embed_options={'renderer': 'svg'}  # default canvas rendering, change to svg rendering
            )

print('\n\n\n ################## new_viz.html has been updated ################## \n\n\n')

# """
# ####################################################################################################################
# ####################################################################################################################
# ################################################### THE END ########################################################
# ####################################################################################################################
# ####################################################################################################################
# """