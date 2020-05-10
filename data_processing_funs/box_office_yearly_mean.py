import pandas as pd
import numpy as np


def get_year_all(year=2019):
    """
    get the box office data of a whole year
    :param year: default 2019
    :return: a data frame of box office data of each country in the designated year
    """
    from data_processing_funs import box_office_data as bx
    from data_processing_funs import us_box_office_data as usbx

    box_office_all = bx.get_all_box_office_df(year)
    us_box_office_all = usbx.us_box_office_cleaner(year)

    box_office_all_full = box_office_all.merge(us_box_office_all, left_on='date', right_on='date')

    return box_office_all_full


def get_year_mean(year=2019):
    """
    call the former function to get a year's box office data;
    get the mean value of each country and make it a dictionary;
    turn the dictionary to a data frame and transpose
    :param year: default 2019
    :return: a data frame with two columns: country_code and box_office_[year]_mean
    """
    # call get_year_all function to get each country's box office data of the designated year
    box_office_all_full = get_year_all(year=year)
    # make index and value holder lists
    box_office_year_index = []
    box_office_year_value = []
    # loop through each column (the first date column is skipped)
    # get country code from column names,
    # and get mean box office of each country (column)
    for i in range(1, len(box_office_all_full.columns)):
        col = box_office_all_full.iloc[:, [i]]
        mean = col.mean()
        index = mean.index[0][0:2]
        value = mean.values[0]
        box_office_year_index.append(index)
        box_office_year_value.append(round(value, 0))
        # print(i, mean)
    # combine the index and value list and make a dictionary
    box_office_year_mean_dict = dict(zip(box_office_year_index, box_office_year_value))
    # turn the dictionary to a 1-row data frame, each column represents a country's yearly mean box office
    box_office_year_mean_df = pd.DataFrame(box_office_year_mean_dict, index=[0])
    # transpose the data frame to a 2-column data frame, rename the columns
    box_office_year_mean_df = box_office_year_mean_df.T.reset_index()
    box_office_year_mean_df.columns = ['Country', ('box_office_' + str(year) + '_mean')]
    return box_office_year_mean_df


# # driver codes
# box_office_2019_mean = get_year_mean(2019)