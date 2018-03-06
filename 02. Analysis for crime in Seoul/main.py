import numpy as np
import pandas as pd
import googlemaps

crime_anal_police = pd.read_csv('Data/02. crime_in_Seoul.csv', thousands=',', encoding='euc-kr')
print(crime_anal_police.head())

gmaps_key = "AIzaSyD0kNaKi5llwVekMVXUrtSFx0MelmGkuOs"
gmaps = googlemaps.Client(key=gmaps_key)
#print(gmaps.geocode('서울중부경찰서', language='ko'))

station_name = []
for name in crime_anal_police['관서명']:
    station_name.append('서울' + str(name[:-1]) + '경찰서')

print(station_name)
station_address = []
station_lat = []
station_lng = []

for name in station_name:
    tmp = gmaps.geocode(name, language='ko')
    station_address.append(tmp[0].get("formatted_address"))

    tmp_loc = tmp[0].get("geometry")
    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])

    print(name + '-->' + tmp[0].get("formatted_address"))