import pandas as pd
import geopandas as gpd
import json


def open_geojson(file_path):
    with open(file_path) as json_data:
        d = json.load(json_data)
    return d


def get_gpd_df(file_path, use_shape_file=True):
    """
    use geo pandas to read GIS files
    modified from A Gordon's function
    https://medium.com/dataexplorations/creating-choropleth-maps-in-altair-eeb7085779a1
    :param file_path:
    :param use_shape_file: whether use geojson or shapefile
    :return:
    """
    if use_shape_file:
        gdf = gpd.read_file(file_path)
    else:
        toronto_json = open_geojson()
        gdf = gpd.GeoDataFrame.from_features(toronto_json)
    return gdf


country_map = 'data/countries/ne_10m_admin_0_countries_lakes.shp'
df = pd.read_csv('_______')
country_map = country_map.merge(df, left_on='AREA_NAME', right_on='neighbourhood', how='inner')