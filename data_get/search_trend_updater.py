import pandas as pd
import numpy as np
from data_processing_funs import search_trend_data as st

base0424 = pd.read_csv('data_get/alt_data_sources/search_trends_20200424.csv')
new0508 = st.merge_trend_data()

"""
20200508_TEST
"""
base_df = base0424.copy()
to_update = new0508.copy()

for i in to_update.index:
    print(i)







# search_trend_data = merge_trend_data()
# print(search_trend_data)

# search_trend_data.to_csv('data/search_trends_20200503.csv')