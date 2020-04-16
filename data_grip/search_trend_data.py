import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# install required
# pip install pytrends
import requests
from bs4 import BeautifulSoup

######
# Country Code Scraper #####
######

url = 'https://www.iban.com/country-codes'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')

# soup testing #####
# # print(soup.prettify())
# # [type(item) for item in list(soup.children)]
# # children[5] is the nested tags
# html = list(soup.children)[5]
# # [type(item) for item in html]
# # children[4] is <body>
# body = list(html.children)[4]
# list(body.children)

# create an empty data frame to hold country code info
column_names = ["country", "alpha_2", "alpha_3", "numeric"]
country_code_table = pd.DataFrame(columns=column_names)

# loop through all trs and append inside tds to country_code data frame as rows
for tr in soup.find_all('tr')[1:]:
    tds = tr.find_all('td')
    td_list = [tds[0].text, tds[1].text, tds[2].text, tds[3].text]
    # print(td_list)
    new_row = pd.Series(td_list)
    country_code_table = country_code_table.append(
        pd.Series(td_list, index=country_code_table.columns),
        ignore_index=True
    )

print(country_code_table)

######
# Country Code Scraper #####
# END #####
######


# with the given country code table:
# this function returns selected country code with the given country name, default alpha_2 code
def get_country_code(country_name, code_type='alpha_2'):
    code_table = country_code_table
    country_code_series = code_table[code_type].loc[code_table['country'] == country_name]
    for country_code in country_code_series:
        return country_code


# this function returns google trend of "coronavirus" in the past 3 month within a given country
def get_google_trends(country_name):
    from pytrends.request import TrendReq
    country_code = get_country_code(country_name)
    pytrend = TrendReq()
    keywords = ['coronavirus']
    pytrend.build_payload(kw_list=keywords, timeframe='today 3-m', geo=country_code)
    # get past 3 month of trend from today
    # search more than three month will return weekly accumulated results
    # data storing needed
    df = pytrend.interest_over_time()
    df = pd.DataFrame(df)
    return df


def trend_data_clean():
    df = get_google_trends()
    df2 = df.reset_index()
    return df2


test1 = trend_data_clean()

#####
# WHAT NEXT #####
# need country name processor #####
# to analyze country names in the other tables #####
#####