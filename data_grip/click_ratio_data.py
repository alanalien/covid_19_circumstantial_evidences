import pandas as pd
from xml.etree import ElementTree as et
import requests

url = "https://awis.api.alexa.com/api?" \
       "Action=TrafficHistory" \
       "&Range=31" \
       "&ResponseGroup=History" \
       "&Url=https://www.who.int/" \
       "&Start=20200301"

payload = {}
headers = {
  'x-api-key': 'HxMdtEu7D11gnzv99BOcA55r3gYK97IK8yluYGae'
}

response = requests.request("GET", url, headers=headers, data=payload)
awis_xml_str = response.text.encode('utf8')

# parse directly from texts instead of file
# root = ET.XML(awis_xml_str)
root = et.fromstring(awis_xml_str)

# # check xml structure
for child in root:
    print(child.tag)
    for child2 in child:
        print("\t" + child2.tag)
        for child3 in child2:
            print("\t\t" + child3.tag)
            for child4 in child3:
                print("\t\t\t" + child4.tag)
                for child5 in child4:
                    print("\t\t\t\t" + child5.tag)
                    for child6 in child5:
                        print("\t\t\t\t\t" + child6.tag)
# OperationRequest
# 	RequestId
# Results
# 	Result
# 		Alexa
# 			Request
# 				Arguments
# 					Argument
#                     Argument
#                     ...
# 					Argument
# 			TrafficHistory
# 				Range
# 				Site
# 				Start
# 				HistoricalData
# 					Data
#                   Data
#                   Data
# 					...
# 					Data
# 	ResponseStatus
# 		StatusCode


for results in root.findall('Results'):
    for result in results.findall('Result'):
        for alexa in result.findall('Alexa'):
            for trafficHistory in alexa.findall('TrafficHistory'):
                for historicalData in trafficHistory.findall('HistoricalData'):
                    # print(historicalData.text)
                    historical_data = et.tostring(historicalData)

root2 = et.fromstring(historical_data)

# for data in root2:
#     for dates in data.findall('Date'):
#         print(dates.text)
#     for pageViews in data.findall('PageViews'):
#         for per_million in pageViews.findall('PerMillion'):
#             print('per_million' + per_million.text)
#         for per_user in pageViews.findall('PerUser'):
#             print('per_user' + per_user.text)


# <Data>
#     <Date>2020-03-01</Date>
#     <PageViews>
#         <PerMillion>130</PerMillion>
#         <PerUser>2.10</PerUser>
#     </PageViews>
#     <Rank>279</Rank>
#     <Reach>
#         <PerMillion>2000</PerMillion>
#     </Reach>
# </Data>
# for data in root2:
#     date = data.find("Date").text
#     print(date)
#     for page_view in data.findall("PageViews"):
#         ppm = page_view.find("PerMillion").text  # page view per million
#         print(ppm)
#         ppu = page_view.find("PerUser").text  # page view per user
#         print(ppu)
#     rank = data.find("Rank").text
#     print(rank)
#     for reach in data.findall("Reach"):
#         rpm = reach.find("PerMillion").text
#         print(rpm)
#     new_row = [date, ppm, ppu, rank, rpm]

column_names = ["Date", "Page_View_Per_Million", "Page_View_Per_User", "Rank", "Reach_Per_Million"]
click_ratio_table = pd.DataFrame(columns=column_names)

for data in root2:
    date = data[0].text
    ppm = data[1][0].text
    ppu = data[1][1].text
    rank = data[2].text
    rpm = data[3][0].text
    new_row = [date, ppm, ppu, rank, rpm]
    click_ratio_table.loc[len(click_ratio_table)] = new_row
