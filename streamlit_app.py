import streamlit as st
import pygsheets
import pandas as pd
from datetime import datetime, date, timedelta
from entsoe import EntsoePandasClient
import seaborn as sns

st.title('ENTSOE-E API')
streamlit run streamlit_app.py
# Connecting to ENTSO-E API

client = EntsoePandasClient(api_key='4b1229d3-1c2c-4fbb-9e43-4d1692208b57')

# timestamps
today = datetime.today()
PreviousDay = (today  - timedelta(days = 1)).strftime('%Y%m%d')
start = pd.Timestamp(PreviousDay, tz='Europe/Brussels')
end = pd.Timestamp(today, tz='Europe/Brussels')

# QUERY 2: Day Ahead Prices

Countries = ['PT','ES','FR','DE_LU','BE','CZ','IT_NORD','AT','NL','SK','FI','CH','PL','GR','EE','HU','RO','LT','LV','NO_1','RS','SI']

Prices = []

for i in Countries:
    Query = client.query_day_ahead_prices(i, start=start,end=end).to_frame() # Prices Query
    Query['Country'] = i
    Prices.append(Query)

Prices = pd.concat(Prices)

#Adding Luxembourg

Price_Luxembourg = client.query_day_ahead_prices('DE_LU', start=start,end=end).to_frame()
Price_Luxembourg['Country']="LU"
Prices = pd.concat([Prices,Price_Luxembourg])

#Replacing wrong country codes

Prices['Country'].replace(to_replace= 'DE_LU',value='DE', inplace= True)
Prices['Country'].replace(to_replace= 'IT_NORD',value='IT', inplace= True)
Prices['Country'].replace(to_replace= 'NO_1',value='NO', inplace= True)
Prices['Country'].replace(to_replace= 'GB',value='UK', inplace= True)

Prices['Date'] = Prices.index.astype(str).str[:-6]
Prices['Date'] = pd.to_datetime(Prices['Date'])

#Unpitoving for Tableau format
Prices_unpivoted = Prices.melt(id_vars = ['Country','Date'])


# google sheets authentication
#creds = '/Users/brunoluis/Jupyter/Projects /ENTSO API/root-gist-358222-ff123e36322d.json'
#api = pygsheets.authorize(service_file=creds)
#wb = api.open('ENTSO-E')

# open the sheet by name
#sheet = wb.worksheet_by_title('Price')
#sheet.set_dataframe(Prices_unpivoted, (1,1))


sns.set(rc={'figure.figsize':(12,9)})
print(sns.lineplot(data = Prices_unpivoted,x = 'Date', y = 'value', hue = 'Country'))
