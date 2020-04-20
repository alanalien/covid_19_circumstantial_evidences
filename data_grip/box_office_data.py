import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import re
import time
import matplotlib.pyplot as plt

######
# Country Code Scraper #####
######

"""
URL PARAMETER SCRAPER
"""

main_url = 'https://www.boxofficemojo.com/intl/?ref_=bo_nb_wew_tab'
main_page = requests.get(main_url)
main_soup = BeautifulSoup(main_page.content, 'html.parser')


country_list = []
code_list = []
for select in main_soup.find_all('select')[0:]:
    option = select.find_all('option')
    for i in option:
        # print(i['value'], i.text)
        match = re.findall('(?<==).*$', i['value'])  # (?<=\=) positively look for characters behind '\='
        code = ''.join(match)
        name = i.text
        country_list.append(name)
        code_list.append(code)

mojo_countries = pd.DataFrame({'country_name': country_list, 'country_code': code_list})
mojo_countries.drop(mojo_countries[mojo_countries['country_code'] == 'FOREIGN'].index, inplace=True)

"""
PAGE SCRAPER
"""


def box_office_scraper(country_code):
    # url prams...
    url = "https://www.boxofficemojo.com/weekend/by-year/2020/?area="
    country_code = country_code  # argument: country code
    page = requests.get(url + country_code)
    soup = BeautifulSoup(page.content, 'html.parser')
    # create an empty data frame to hold country code info
    column_names = ["date",
                    "top_10_gross",
                    "top_10_last_week_compare",
                    "overall_gross",
                    "overall_last_week_compare",
                    "releases",
                    "#1_release",
                    "week"]
    box_office_table = pd.DataFrame(columns=column_names)

    # loop through all trs and append inside tds to country_code data frame as rows
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        td_list = [tds[0].text,
                   tds[1].text,
                   tds[2].text,
                   tds[3].text,
                   tds[4].text,
                   tds[5].text,
                   tds[6].text,
                   tds[10].text]
        # print(td_list)
        # new_row = pd.Series(td_list)
        box_office_table = box_office_table.append(
            pd.Series(td_list, index=box_office_table.columns),
            ignore_index=True
        )
    return box_office_table


def box_office_cleaner(country_code):
    box_office_table = box_office_scraper(country_code)  # call former function to scrape box office data
    box_office_table = box_office_table.iloc[:, [0, 3, 7]]  # select only useful columns

    # append formatted date column
    week_list = box_office_table.iloc[:, 2]  # get week number

    date_list = []
    for week_num in week_list:
        first_sunday = datetime.strptime('2020-01-05', '%Y-%m-%d')
        day_diff = (int(week_num)-1)*7
        new_date = first_sunday + timedelta(days=day_diff)
        new_date = datetime.date(new_date)
        date_list.append(new_date)

    box_office_table.insert(0, 'new_date', date_list, True)

    box_office_table = box_office_table.iloc[:, [0, 2]]
    box_office_table.columns = ['date', country_code]
    box_office_table = box_office_table.set_index(box_office_table['date'])
    box_office_table = pd.DataFrame(box_office_table)
    box_office_table = box_office_table.iloc[:,[1]]
    box_office_table = box_office_table.add_suffix('_boxOffice_total')
    return box_office_table


"""
BREAK
the following is an iteration that uses functions above,
which returns a data frame with total gross of all countries
listed on the mojo box office website
"""


# create empty data frame with sundays as index
def last_sunday(today):
    today = datetime.date(today)
    d = today.toordinal()
    last = d - 6
    sundays = last - (last % 7)
    sunday = datetime.date(datetime.fromordinal(sundays))
    return sunday


def sunday_df():
    sundays = []
    today = datetime.now()
    last_sunday_result = last_sunday(today)
    week_num = int(int(today.strftime('%j')) / 7)  # %j represent the day of the year
    w = -1
    while w <= (week_num-1):
        sundays.append(last_sunday_result - timedelta(w*7))
        w = w+1
        # print(w)
    df = pd.DataFrame(sundays, columns=['date'])
    return df  # a data frame with only one column of dates is returned


# call sunday_df to create an empty data frame
box_office_df = sunday_df()
box_office_df = box_office_df.set_index(box_office_df['date'])

# test = ['IT', 'AL', 'VN']
# for idx, my_codes in enumerate(test):
for idx, my_codes in enumerate(mojo_countries.loc[:, 'country_code']):
    # scrape each country's box office data
    box_office_data = box_office_cleaner(my_codes)

    # clean box office data, make $449,007 format to int
    box_office_data_list = box_office_data.iloc[:, 0].tolist()
    box_office_num_list = []
    for usd in box_office_data_list:
        usd = usd[1:]
        usd = usd.replace(',', '')
        usd = int(usd)
        # print(usd)
        box_office_num_list.append(usd)
    box_office_data.insert(0, '_'.join([my_codes, 'boxOffice_usd']), box_office_num_list, True)
    box_office_df[my_codes + '_boxOffice_usd'] = box_office_data.iloc[:, [0]]

    print('done', my_codes, '------', idx, '/ 92')
    time.sleep(3)


plt.cla()
box_office_df.loc[:, :].plot()


"""
TO BE UPDATE:
drop 'central america', 'east africa' and 'international' rows;
sum 2 switzerland rows;
rename russia/cis;
drop 'CN' (China) and use alter data source;
"""

for index, rows in mojo_countries.iterrows():  # iterrows does not preserve dtypes across the rows
    if len(rows['country_code']) > 2:
        print(rows['country_name'], rows['country_code'])

# Central America XC4
# East Africa XKN
# International FOREIGN
# Russia/CIS XR2
# Serbia and Montenegro XS2
# Switzerland (French) XS3
# Switzerland (German) XS1
