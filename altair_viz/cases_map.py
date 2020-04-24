import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# below are for mapping purpose
import geopandas as gpd
import shapefile
import dbfpy
# arcpy might be better if have access
# https://gis.stackexchange.com/questions/44692/accessing-attribute-table-within-shapefile-and-replace-values
import zipfile
import requests
import io

import altair as alt
import datetime as dt
alt.renderers.enable('html')


test2 = test1.loc[:, ['China_test1', 'US_test1', 'Italy_test1', 'Korea,South_test1']]

shape_url = \
    'https://www.naturalearthdata.com/' \
    'http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries_lakes.zip'

local_path = 'temp/'
print('Downloading shapefile...')
r = requests.get(shape_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
print("Done")
z.extractall(path=local_path)  # extract to folder
filenames = [y for y in sorted(z.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)]
print(filenames)

dbf, prj, shp, shx = [filename for filename in filenames]
baseMap = gpd.read_file(local_path + shp)
print("Shape of the dataframe: {}".format(baseMap.shape))
print("Projection of dataframe: {}".format(baseMap.crs))
# baseMap.tail()

ax = baseMap.plot()
# ax.set_title("USA Counties. Default view)");

# import shapefile
# https://pypi.org/project/pyshp/#reading-records
sf = shapefile.Reader("temp/ne_10m_admin_0_countries_lakes.shp")
fields = sf.fields
records = sf.records()
len(records)

rec = sf.record(3)
print(rec['ISO_A2'])

plt.figure()
for shape in sf.shapeRecords():
    x = [i[0] for i in shape.shape.polygon[:]]
    y = [i[1] for i in shape.shape.polygon[:]]
    plt.plot(x, y)
plt.show()

"""
OBSTACLES:
arcpy is not available (need arcgis license and windows;
and dbfpy is based on python2
"""