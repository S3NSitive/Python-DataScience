import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import platform
import json
import folium
import googlemaps
import numpy as np
import warnings
from matplotlib import font_manager, rc
from selenium import webdriver
from tqdm import tqdm
from glob import glob
'''
## Naver Login
driver = webdriver.Chrome('Driver/chromedriver.exe')
driver.get("https://nid.naver.com/nidlogin.login")

driver.find_element_by_id("id").send_keys("doble0309")
driver.find_element_by_id("pw").send_keys("privacy!@34")

driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()

## Naver Mail
driver.get("https://mail.naver.com/")

driver.find_element_by_xpath('//*[@id="nav_snb"]/div[1]/a[1]/strong').click()
driver.find_element_by_name("toInput").send_keys("doble0309")
driver.find_element_by_name("subject").send_keys("doble0309")

driver = webdriver.Chrome('Driver/chromedriver.exe')
driver.get("http://www.opinet.co.kr/searRgSelect.do")

gu_list_raw = driver.find_element_by_xpath('//*[@id="SIGUNGU_NM0"]')
gu_list = gu_list_raw.find_elements_by_tag_name('option')
gu_names = [option.get_attribute('value') for option in gu_list]
gu_names.remove('')

pbar = tqdm(gu_names)
for gu in pbar:
    pbar.set_description("%s index add" % gu)

    driver.find_element_by_id("SIGUNGU_NM0").send_keys(gu)
    time.sleep(2)

    driver.find_element_by_xpath('//*[@id="searRgSelect"]').click()
    time.sleep(2)

    driver.find_element_by_xpath('//*[@id="glopopd_excel"]').click()
    time.sleep(2)

driver.close()
'''
station_files = glob('Data/지역*.xls')

tmp_raw = []

for file_name in station_files:
    tmp = pd.read_excel(file_name, header=2)
    tmp_raw.append(tmp)

station_raw = pd.concat(tmp_raw)
stations = pd.DataFrame({'Oil_store':station_raw['상호'],
                         '주소':station_raw['주소'],
                         '가격':station_raw['휘발유'],
                         '셀프':station_raw['셀프여부'],
                         '상표':station_raw['상표']})
stations['구'] = [eachAddress.split()[1] for eachAddress in stations['주소']]
stations.loc[stations['구'] == '서울특별시', '구'] = '성동구'
stations.loc[stations['구'] == '특별시', '구'] = '도봉구'
stations = stations[stations['가격'] != '-']
stations['가격'] = [float(value) for value in stations['가격']]
stations.reset_index(inplace=True)
del stations['index']

path = "c:/Windows/Fonts/malgun.ttf"

if platform.system() == "Darwin":
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:\Windows\Fonts\malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')
'''
plt.figure(figsize=(10, 6))
sns.boxplot(x='상표', y='가격', data=stations, palette='Set3')
sns.swarmplot(x='상표', y='가격', data=stations, color='.6')
plt.show()
'''
warnings.simplefilter(action='ignore', category=FutureWarning)

gu_data = pd.pivot_table(stations, index=['구'], values=['가격'], aggfunc=np.mean)
'''
geo_path = '../02. Analysis for crime in Seoul/Data/02. skorea_municipalities_geo_simple.json'
geo_data = json.load(open(geo_path, encoding='utf-8'))

map = folium.Map(location=[37.5502, 126.982], zoom_start=10.5,
                 tiles='Stamen Toner')
map.choropleth(geo_data=geo_data,
               data=gu_data,
               columns=[gu_data.index, '가격'],
               fill_color='PuRd',
               key_on='feature.id')
map.save('Data/04. map.html')
'''
oil_price_top10 = stations.sort_values(by='가격', ascending=False).head(10)
oil_price_bottom10 = stations.sort_values(by='가격', ascending=True).head(10)

gmap_key = 'AIzaSyD0kNaKi5llwVekMVXUrtSFx0MelmGkuOs'
gmaps = googlemaps.Client(key=gmap_key)

lat = []
lng = []
pbar = tqdm(oil_price_top10.index)

for n in pbar:
    pbar.set_description('%d indexing' % n)
    try:
        tmp_add = str(oil_price_top10['주소'][n]).split('(')[0]
        tmp_map = gmaps.geocode(tmp_add)

        tmp_loc = tmp_map[0].get('geometry')
        lat.append(tmp_loc['location']['lat'])
        lng.append(tmp_loc['location']['lng'])
    except:
        lat.append(np.nan)
        lng.append(np.nan)
        print('Here is nan!')

oil_price_top10['lat'] = lat
oil_price_top10['lng'] = lng

lat = []
lng = []
pbar = tqdm(oil_price_bottom10.index)

for n in pbar:
    pbar.set_description('%d indexing' % n)
    try:
        tmp_add = str(oil_price_bottom10['주소'][n]).split('(')[0]
        tmp_map = gmaps.geocode(tmp_add)

        tmp_loc = tmp_map[0].get('geometry')
        lat.append(tmp_loc['location']['lat'])
        lng.append(tmp_loc['location']['lng'])
    except:
        lat.append(np.nan)
        lng.append(np.nan)
        print('Here is nan!')

oil_price_bottom10['lat'] = lat
oil_price_bottom10['lng'] = lng

map = folium.Map(location=[37.5202, 126.975], zoom_start=10.5)

for n in oil_price_top10.index:
    if pd.notnull(oil_price_top10['lat'][n]):
        folium.CircleMarker([oil_price_top10['lat'][n], oil_price_top10['lng'][n]],
                            radius=15, color='#CD3181',
                            fill_color='#CD3181', fill=True).add_to(map)

for n in oil_price_bottom10.index:
    if pd.notnull(oil_price_bottom10['lat'][n]):
        folium.CircleMarker([oil_price_bottom10['lat'][n], oil_price_bottom10['lng'][n]],
                            radius=15, color='#3186cc',
                            fill_color='#3186cc', fill=True).add_to(map)

map.save('Data/04. map.html')