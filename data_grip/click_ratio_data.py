import pandas as pd
from xml.etree import ElementTree as ET
import requests
from datetime import datetime

q_range = {'Range': 1}
q_resp_group = {'ResponseGroup': 'History'}
q_url_WHO = {'https://www.who.int/'}
q_date = datetime.date(datetime.now())

url = "https://awis.api.alexa.com/api?" \
       "Action=TrafficHistory" \
       "&Range=31" \
       "&ResponseGroup=History" \
       "&Url=https://www.who.int/"\
       "&Start=20200301"\

payload = {}
headers = {
  'x-api-key': '''
  ### your_api_key_here ###
  '''
}

response = requests.request("GET", url, headers=headers, data=payload)
awis_xml_str = response.text.encode('utf8')

# parse directly from texts instead of file
root = ET.fromstring(awis_xml_str)

column_names = ["Date", "Page_View_Per_Million", "Page_View_Per_User", "Rank", "Reach_Per_Million"]
click_ratio_table = pd.DataFrame(columns=column_names)


for results in root.findall('Results'):
    for result in results.findall('Result'):
        for alexa in result.findall('Alexa'):
            for trafficHistory in alexa.findall('TrafficHistory'):
                for historicalData in trafficHistory.findall('HistoricalData'):
                    historical_data = ET.tostring(historicalData)

root2 = ET.fromstring(historical_data)


for data in root2:
    date = data[0].text
    ppm = data[1][0].text
    ppu = data[1][1].text
    rank = data[2].text
    rpm = data[3][0].text
    new_row = [date, ppm, ppu, rank, rpm]
    click_ratio_table.loc[len(click_ratio_table)] = new_row

print(click_ratio_table)
