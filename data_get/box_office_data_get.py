import pandas as pd
from data_clean_funs import box_office_data as bx, us_box_office_data as usbx

box_office = bx.get_all_box_office_df()
us_box_office = pd.read_csv("data_get/alt_data_sources/us_box_office_2020_by_weekend.csv")
box_office['date'] = pd.to_datetime(box_office['date'])
us_box_office['date'] = pd.to_datetime(us_box_office['date'])
box_office_full = pd.merge(box_office, us_box_office, left_on='date', right_on='date')


# some country codes that mojo used were not following the ISO standard:

# mojo_countries = bx.mojo_country_codes()
# for index, rows in mojo_countries.iterrows():
#     if len(rows['country_code']) > 2:
#         print(rows['country_name'], rows['country_code'])
#
# # Central America XC4
# # East Africa XKN
# # International FOREIGN -- removed
# # Russia/CIS XR2
# # Serbia and Montenegro XS2
# # Switzerland (French) XS3
# # Switzerland (German) XS1

# # sum 2 sub division of Switzerland box office
# box_office_full['CH_boxOffice_usd'] = \
#     box_office_full['XS1_boxOffice_usd'].fillna(0) + box_office_full['XS3_boxOffice_usd']
# switzerland already has an independent page, therefore removed

# Russia and CIS are considered russia only
# Russia has its own page but empty, make Russia/CIS RU
box_office_full['RU_boxOffice_usd'] = box_office_full['XR2_boxOffice_usd']
# Serbia and Montenegro are considered as Serbia only
box_office_full['RS_boxOffice_usd'] = box_office_full['XS2_boxOffice_usd']

# drop redundant columns
to_drop = ['XC4', 'XKN', 'XR2', 'XS2', 'XS3', 'XS1']
for i in to_drop:
    c = i + '_boxOffice_usd'
    # print(c)
    box_office_full = box_office_full.drop([c], axis=1)

box_office_full.to_csv('data/box_office_full.csv', index=False)

# # test
# import matplotlib.pyplot as plt
# plt.cla()
# for i in box_office_full.iloc[:, 1:]:
#     plt.plot(box_office_full.iloc[:, 0], box_office_full.loc[:, i])