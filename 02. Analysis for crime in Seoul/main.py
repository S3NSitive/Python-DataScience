import numpy as np
import pandas as pd
import googlemaps
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import folium
import json
from sklearn import preprocessing
from matplotlib import font_manager, rc


crime_anal_police = pd.read_csv('Data/02. crime_in_Seoul.csv', thousands=',', encoding='euc-kr')
print(crime_anal_police.head())

gmaps_key = "AIzaSyD0kNaKi5llwVekMVXUrtSFx0MelmGkuOs"
gmaps = googlemaps.Client(key=gmaps_key)
#print(gmaps.geocode('서울중부경찰서', language='ko'))

station_name = []
for name in crime_anal_police['관서명']:
    station_name.append('서울' + str(name[:-1]) + '경찰서')

print(station_name)
print()
station_address = []
station_lat = []
station_lng = []

for name in station_name:
    tmp = gmaps.geocode(name, language='ko')
    station_address.append(tmp[0].get("formatted_address"))

    tmp_loc = tmp[0].get("geometry")
    station_lat.append(tmp_loc['location']['lat'])
    station_lng.append(tmp_loc['location']['lng'])

    #print(name + '-->' + tmp[0].get("formatted_address"))

gu_name = []
for name in station_address:
    tmp = name.split()

    tmp_gu = [gu for gu in tmp if gu[-1] == '구'][0]

    gu_name.append(tmp_gu)

crime_anal_police['구별'] = gu_name
crime_anal_police.loc[crime_anal_police['관서명'] == '금천서', ['구별']] = '금천구'
crime_anal_police[crime_anal_police['관서명'] == '금천서']
print(crime_anal_police.head())
'''
crime_anal_police.to_csv('Data/02. crime_in_Seoul_include_gu_name.csv',
                         sep=',', encoding='utf-8')
'''
crime_anal_raw = pd.read_csv('Data/02. crime_in_Seoul_include_gu_name.csv',
                             encoding='utf-8', index_col=0)
crime_anal = pd.pivot_table(crime_anal_raw, index='구별', aggfunc=np.sum)
crime_anal['강간 검거율'] = crime_anal['강간 검거'] / crime_anal['강간 발생'] * 100
crime_anal['강도 검거율'] = crime_anal['강도 검거'] / crime_anal['강도 발생'] * 100
crime_anal['살인 검거율'] = crime_anal['살인 검거'] / crime_anal['살인 발생'] * 100
crime_anal['절도 검거율'] = crime_anal['절도 검거'] / crime_anal['절도 발생'] * 100
crime_anal['폭력 검거율'] = crime_anal['폭력 검거'] / crime_anal['폭력 발생'] * 100

del crime_anal['강간 검거']
del crime_anal['강도 검거']
del crime_anal['살인 검거']
del crime_anal['절도 검거']
del crime_anal['폭력 검거']

con_list = ['강간 검거율', '강도 검거율', '살인 검거율', '절도 검거율', '폭력 검거율']

for column in con_list:
    crime_anal.loc[crime_anal[column] > 100, column] = 100

crime_anal.rename(columns = {'강간 발생':'강간',
                            '강도 발생':'강도',
                            '살인 발생':'살인',
                            '절도 발생':'절도',
                            '폭력 발생':'폭력'}, inplace=True)

col = ['강간', '강도', '살인', '절도', '폭력']

x = crime_anal[col].values
min_max_scaler = preprocessing.MinMaxScaler()

x_scaled = min_max_scaler.fit_transform(x.astype(float))
crime_anal_norm = pd.DataFrame(x_scaled, columns=col, index=crime_anal.index)
col2 = ['강간 검거율', '강도 검거율', '살인 검거율', '절도 검거율', '폭력 검거율']
crime_anal_norm[col2] = crime_anal[col2]

result_CCTV = pd.read_csv('Data/01. CCTV_result.csv',
                          encoding='UTF-8', index_col='구별')
crime_anal_norm[['인구수', 'CCTV']] = result_CCTV[['인구수', '소계']]

crime_anal_norm['범죄'] = np.sum(crime_anal_norm[col], axis=1)
crime_anal_norm['검거'] = np.sum(crime_anal_norm[col2], axis=1)
print(crime_anal_norm.head())
'''
path = "c:/Windows/Fonts/malgun.ttf"

if platform.system() == "Darwin":
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:\Windows\Fonts\malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')

target_col = ['강간', '강도', '살인', '절도', '폭력', '범죄']

crime_anal_norm['범죄'] = crime_anal_norm['범죄'] / 5
crime_anal_norm_sort = crime_anal_norm.sort_values(by='범죄', ascending=False)

plt.figure(figsize=(10, 6))
sns.set(style="ticks")
sns.heatmap(crime_anal_norm_sort[target_col], annot=True, fmt='f', linewidths=.5)
plt.title('범죄 비율 (정규화된 발생 건수로 정렬)')
plt.show()

crime_anal_norm.to_csv('Data/02. crime_in_Seoul_final.csv', sep=',', encoding='utf-8')
'''

geo_path = 'Data/02. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

map = folium.Map(location=[37.5502, 126.982], zoom_start=11)
map.choropleth(geo_data=geo_str, data=crime_anal_norm['범죄'],
               columns=[crime_anal_norm.index, crime_anal_norm['범죄']],
               fill_color='PuRd', #PuRd, YlGnBu
               key_on='feature.id')

crime_anal_raw['lat'] = station_lat
crime_anal_raw['lng'] = station_lng

col3 = ['살인 검거', '강도 검거', '강간 검거', '절도 검거', '폭력 검거']
tmp = crime_anal_raw[col3] / crime_anal_raw[col3].max()

crime_anal_raw['검거'] = np.sum(tmp, axis=1)

for n in crime_anal_raw.index:
    folium.CircleMarker([crime_anal_raw['lat'][n], crime_anal_raw['lng'][n]],
                        radius=crime_anal_raw['검거'][n]*10, popup=crime_anal_raw['관서명'][n],
                        color='#3186cc', fill=True, fill_color='#3186cc').add_to(map)

map.save('Data/02. map.html')