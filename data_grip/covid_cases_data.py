import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# below are for mapping purpose
import geopandas as gpd
import dbfpy
# arcpy might be better if have access
# https://gis.stackexchange.com/questions/44692/accessing-attribute-table-within-shapefile-and-replace-values
import zipfile
import requests
import io


path = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
file1 = "time_series_covid19_confirmed_global.csv"
file2 = "time_series_covid19_deaths_global.csv"
file3 = "time_series_covid19_recovered_global.csv"

confirmed = pd.read_csv(path + file1)
death = pd.read_csv(path + file2)
recovered = pd.read_csv(path + file3)


def date_formatting(df):  # rename columns by date
    from datetime import datetime
    sub_df = df.iloc[:, 1:]
    for i in range(0, len(sub_df.columns)):
        if i <= 2:
            pass
        else:
            date_string = sub_df.columns[i]
            d1 = datetime.date(datetime.strptime(date_string, '%m/%d/%y'))
            d2 = str(d1)
            sub_df.rename(columns={date_string: d2}, inplace=True)
    return sub_df


def country_grouping(df):  # group values by country
    country_group = date_formatting(df)
    country_group.fillna(value=0, inplace=True)
    country_group = country_group.groupby(['Country/Region'])[country_group.columns[3:]].sum().reset_index()
    return country_group


def country_code_update(df):
    """NOTES"""
    """
    # all cruise ship cases have been removed
    # West Bank and Gaza region is considered as part of Palestine (PS)
    # Taiwan is considered separately from China here, for it has potentially different data collection procedure.
    # XK represents Kosovo (XK, XKX, while Kosovo is not listed as an ISO standard country.
    #   The unofficial 2 and 3-digit codes are used by the European Commission and others,
    #   until Kosovo is assigned an ISO code.
    """
    from pycountry import countries as ct
    new_df = country_grouping(df)
    # country names in the data set that are not fit ISO standard
    completion = pd.DataFrame(np.array([['Bolivia', 'BO'],
                                        ['Brunei', 'BN'],
                                        ['Congo (Brazzaville)', 'CG'],
                                        ['Congo (Kinshasa)', 'CD'],
                                        ['Cote d\'Ivoire', 'CI'],
                                        ['Holy See', 'VA'],
                                        ['Iran', 'IR'],
                                        ['Korea, South', 'KR'],
                                        ['Moldova', 'MD'],
                                        ['Russia', 'RU'],
                                        ['Taiwan*', 'TW'],
                                        ['Tanzania', 'TZ'],
                                        ['US', 'US'],
                                        ['Venezuela', 'VE'],
                                        ['Vietnam', 'VN'],
                                        ['Syria', 'SY'],
                                        ['Laos', 'LA'],
                                        ['West Bank and Gaza', 'PS'],
                                        ['Kosovo', 'XK'],
                                        ['Burma', 'MM']
                                        ]),
                              columns=['c_name', 'c_code']
                              )
    country_code_list = []
    for country_name in new_df['Country/Region']:
        try:
            if country_name in completion['c_name'].tolist():
                # print('exception covered: ', country_name)
                country_code = completion['c_code'].loc[completion['c_name'] == country_name].item()
            # identifies the cruise ships in the data set considered as a 'country'
            elif country_name == 'Diamond Princess' or country_name == 'MS Zaandam':
                country_code = 'Cruise Ship'
            else:
                country_code = ct.get(name=country_name).alpha_2
        except Exception:
            print('no result: ', country_name)
            country_code = 'None'
            pass
        country_code_list.append(country_code)
    # print(country_code_list)
    new_df.insert(0, "country_code", country_code_list, True)
    new_df = new_df.drop(columns='Country/Region')
    unknown_index = new_df[new_df['country_code'] == 'Cruise Ship'].index
    new_df.drop(unknown_index, inplace=True)  # drop when country_code = 'None', most likely are Cruise ships
    # new_df.set_index(new_df['country_code'])
    return new_df


def get_df_name(df):  # get data frame name for further usage
    df_name = [i for i in globals() if globals()[i] is df][0]
    # https://stackoverflow.com/questions/31727333/get-the-name-of-a-pandas-dataframe
    return df_name


def remodeling(df):  # transposing, column renaming, and date format converting
    df_name = get_df_name(df)
    new_df = country_code_update(df)
    new_df.rename(columns={'country_code': 'Date'}, inplace=True)
    new_df = new_df.set_index('Date').T  # Date and its value (string) became index
    new_df.index = pd.to_datetime(new_df.index)
    new_df = new_df.add_suffix('_' + df_name)
    # new_df.set_index(new_df['Date'])
    return new_df


CF = remodeling(confirmed)
DT = remodeling(death)
CU = remodeling(recovered)

test = remodeling(confirmed)
# print(test.dtypes)

# for col in test.columns:
#     print(col)

# this gives date value indexed with country

plt.cla()
test.loc[:, ['US_confirmed', 'CN_confirmed']].plot()


"""
MAPPING EXPERIMENTS
"""

# test2 = test1.loc[:, ['China_test1', 'US_test1', 'Italy_test1', 'Korea,South_test1']]

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

"""
OBSTACLES:
arcpy is not available (need arcgis license and windows;
and dbfpy is based on python2

so.
currently unable to combine my data to the attribute table
"""
