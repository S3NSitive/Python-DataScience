from urllib.request import urlopen
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
import pandas as pd
import googlemaps
import folium
import numpy as np
'''
url_base = "http://www.chicagomag.com"
url_sub = "/Chicago-Magazine/November-2015/Best-Pizza/"
url = url_base + url_sub

html = urlopen(url)
soup = BeautifulSoup(html, "html.parser")

rank = []
name = []
main_menu = []
url_add = []

find_rank = soup.find_all('div', 'pizza15-rank')
for rank_list in find_rank:
    rank.append(rank_list.get_text())

find_info = soup.find_all('div', 'pizza15-info')
for info_list in find_info:
    url_add.append(url_base + info_list.find('a')['href'])
    name.append(info_list.find(class_='pizza15-list-link').get_text())
    main_menu.append(info_list.find(class_='leadin').next_sibling[1:])

data = {'Rank':rank, 'Menu':main_menu, 'Cafe':name, 'URL':url_add}
df = pd.DataFrame(data, columns=['Rank', 'Cafe', 'Menu', 'URL'])
print(df.head())
df.to_csv('Data/03. best_pizzas_list_chicago.csv', sep=',', encoding='UTF-8')

df = pd.read_csv('Data/03. best_sandwiches_list_chicago.csv', index_col=0)

price = []
address = []
pbar = tqdm(df.index)

for n in pbar:
    pbar.set_description("%d index add" % n)
    html = urlopen(df['URL'][n])
    soup_tmp = BeautifulSoup(html, "lxml")

    getting = soup_tmp.find('p', 'addy').get_text()

    price.append(getting.split()[0][:-1])
    address.append(' '.join(getting.split()[1:-2]))
'''
df = pd.read_csv('Data/03. best_sandwiches_list_chicago2.csv', index_col=0)

gmaps_key = "AIzaSyD0kNaKi5llwVekMVXUrtSFx0MelmGkuOs"
gmaps = googlemaps.Client(key=gmaps_key)

lat = []
lng = []
pbar = tqdm(df.index)

for n in pbar:
    pbar.set_description("%d index add" % n)
    if df['Address'][n] != 'Multiple':
        target_name = df['Address'][n] + ', ' + 'Cicago'
        gmaps_output = gmaps.geocode(target_name)
        location_output = gmaps_output[0].get('geometry')
        lat.append(location_output['location']['lat'])
        lng.append(location_output['location']['lng'])
    else:
        lat.append(np.nan)
        lng.append(np.nan)

df['lat'] = lat
df['lng'] = lng

mapping = folium.Map(location=[df['lat'].mean(), df['lng'].mean()],
                     zoom_start=11)

for n in df.index:
    if df['Address'][n] != 'Multiple':
        folium.Marker([df['lat'][n], df['lng'][n]],
                      popup=df['Cafe'][n]).add_to(mapping)

mapping.save('Data/03. map.html')
