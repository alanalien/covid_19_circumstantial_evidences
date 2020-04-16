import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup

######
# Country Code Scraper #####
######

url = "https://www.boxofficemojo.com/weekend/by-year/2020/?area="
country_code = "IT"
page = requests.get(url+country_code)
soup = BeautifulSoup(page.content, 'html.parser')

# create an empty data frame to hold country code info
column_names = ["date",
                "top_10_gross",
                "top_10_last_week_compare",
                "overall_gross",
                "overall_last_week_compare",
                "#1_release",
                "week"]
box_office_table = pd.DataFrame(columns=column_names)

# loop through all trs and append inside tds to country_code data frame as rows
for tr in soup.find_all('tr')[1:]:
    tds = tr.find_all('td')
    td_list = [tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text, tds[6].text]
    # print(td_list)
    new_row = pd.Series(td_list)
    box_office_table = box_office_table.append(
        pd.Series(td_list, index=box_office_table.columns),
        ignore_index=True
    )

print(box_office_table)
box_office_table.iloc[:, [0, 3, 6]].columns()


