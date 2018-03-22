import pandas as pd
import numpy as np
import re
import time
import platform
import matplotlib.pyplot as plt
import folium
import json
import warnings

from matplotlib import font_manager, rc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

warnings.simplefilter(action='ignore', category=FutureWarning)
path = 'c:/Windows/Fonts/malgun.ttf'
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')
'''
plt.rcParams['axes.unicode_minus'] = False

driver = webdriver.Chrome('Driver/chromedriver.exe')
driver.get("http://info.nec.go.kr/main/showDocument.xhtml?electionId=0000000000&topMenuId=VC&secondMenuId=VCCP09")

driver.find_element_by_id("electionType1").click()
driver.find_element_by_id("electionName").send_keys("제19대")
time.sleep(1)
driver.find_element_by_id("electionCode").send_keys("대통령선거")

sido_list_raw = driver.find_element_by_xpath('//*[@id="cityCode"]')
time.sleep(1)
sido_list = sido_list_raw.find_elements_by_tag_name("option")
sido_name_values = [option.text for option in sido_list]
sido_name_values = sido_name_values[2:]
print(sido_name_values)

wait = WebDriverWait(driver, 10)

election_result_raw = {'광역시도' : [],
                       '시군' : [],
                       'pop' : [],
                       'moon' : [],
                       'hong' : [],
                       'ahn' : []}

def get_num(tmp):
    return float(re.split('\(', tmp)[0].replace(',',''))

def move_sido(name):
    element = driver.find_element_by_id("cityCode")
    element.send_keys(name)
    make_xpath = '//*[@id="searchBtn"]'
    wait.until(EC.element_to_be_clickable((By.XPATH,make_xpath)))
    driver.find_element_by_xpath(make_xpath).click()

def append_data(df, sido_name, data):
    for each in df[0].values[1:]:
        data['광역시도'].append(sido_name)
        data['시군'].append(each[0])
        data['pop'].append(each[2])
        data['moon'].append(each[3])
        data['hong'].append(each[4])
        data['ahn'].append(each[5])

for each_sido in sido_name_values:
    move_sido(each_sido)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')

    df = pd.read_html(str(table))

    append_data(df, each_sido, election_result_raw)

election_result = pd.DataFrame(election_result_raw,
                               columns=['광역시도', '시군', 'pop', 'moon', 'hong', 'ahn'])
print(election_result.head())

election_result.to_csv('Data/06. election_result.csv', encoding='utf-8', sep=',')
driver.close()
'''
election_result = pd.read_csv('Data/06. election_result.csv', encoding='utf-8', index_col=0)

sido_candi = election_result['광역시도']
sido_candi = [name[:2] if name[:2] in ['서울', '부산', '대구', '광주', '인천', '대전', '울산']
              else '' for name in sido_candi]

def cut_char_sigu(name):
    return name if len(name)==2 else name[:-1]

sigun_candi = ['']*len(election_result)

for n in election_result.index:
    each = election_result['시군'][n]
    if each[:2] in ['수원', '성남', '안양', '안산', '고양', '용인', '청주',
                        '천안', '전주', '포항', '창원']:
        sigun_candi[n] = re.split('시', each)[0]+' '+cut_char_sigu(re.split('시', each)[1])
    else:
        sigun_candi[n] = cut_char_sigu(each)

ID_candi = [sido_candi[n]+' '+sigun_candi[n] for n in range(0, len(sigun_candi))]
ID_candi = [name[1:] if name[0] == ' ' else name for name in ID_candi]
ID_candi = [name[:2] if name[:2] == '세종' else name for name in ID_candi]

election_result['ID'] = ID_candi

election_result[['rate_moon', 'rate_hong', 'rate_ahn']] = \
    election_result[['moon', 'hong', 'ahn']].div(election_result['pop'], axis=0)
election_result[['rate_moon', 'rate_hong', 'rate_ahn']] *= 100

draw_korea = pd.read_csv('Data/06. draw_korea.csv', encoding='utf-8', index_col=0)

election_result.loc[125, 'ID'] = '고성(강원)'
election_result.loc[233, 'ID'] = '고성(경남)'

election_result.loc[228, 'ID'] = '창원 합포'
election_result.loc[229, 'ID'] = '창원 회원'

ahn_temp = election_result.loc[85, 'ahn']/3
hong_temp = election_result.loc[85, 'hong']/3
moon_temp = election_result.loc[85, 'moon']/3
pop_temp = election_result.loc[85, 'pop']/3

rate_moon_tmp = election_result.loc[85, 'rate_moon']
rate_hong_tmp = election_result.loc[85, 'rate_hong']
rate_ahn_tmp = election_result.loc[85, 'rate_ahn']

election_result.loc[250] = [ahn_temp, hong_temp, moon_temp, pop_temp,
                            '경기도', '부천시', '부천 소사',
                            rate_moon_tmp, rate_hong_tmp, rate_ahn_tmp]
election_result.loc[251] = [ahn_temp, hong_temp, moon_temp, pop_temp,
                            '경기도', '부천시', '부천 오정',
                            rate_moon_tmp, rate_hong_tmp, rate_ahn_tmp]
election_result.loc[252] = [ahn_temp, hong_temp, moon_temp, pop_temp,
                            '경기도', '부천시', '부천 원미',
                            rate_moon_tmp, rate_hong_tmp, rate_ahn_tmp]
election_result.drop([85], inplace=True)

final_elect_data = pd.merge(election_result, draw_korea, how='left', on=['ID'])
final_elect_data['moon_vs_hong'] = final_elect_data['rate_moon'] - \
                                                                final_elect_data['rate_hong']
final_elect_data['moon_vs_ahn'] = final_elect_data['rate_moon'] - \
                                                                final_elect_data['rate_ahn']
final_elect_data['ahn_vs_hong'] = final_elect_data['rate_ahn'] - \
                                                                final_elect_data['rate_hong']

BORDER_LINES = [
    [(5, 1), (5,2), (7,2), (7,3), (11,3), (11,0)], # 인천
    [(5,4), (5,5), (2,5), (2,7), (4,7), (4,9), (7,9),
     (7,7), (9,7), (9,5), (10,5), (10,4), (5,4)], # 서울
    [(1,7), (1,8), (3,8), (3,10), (10,10), (10,7),
     (12,7), (12,6), (11,6), (11,5), (12, 5), (12,4),
     (11,4), (11,3)], # 경기도
    [(8,10), (8,11), (6,11), (6,12)], # 강원도
    [(12,5), (13,5), (13,4), (14,4), (14,5), (15,5),
     (15,4), (16,4), (16,2)], # 충청북도
    [(16,4), (17,4), (17,5), (16,5), (16,6), (19,6),
     (19,5), (20,5), (20,4), (21,4), (21,3), (19,3), (19,1)], # 전라북도
    [(13,5), (13,6), (16,6)], # 대전시
    [(13,5), (14,5)], #세종시
    [(21,2), (21,3), (22,3), (22,4), (24,4), (24,2), (21,2)], #광주
    [(20,5), (21,5), (21,6), (23,6)], #전라남도
    [(10,8), (12,8), (12,9), (14,9), (14,8), (16,8), (16,6)], #충청북도
    [(14,9), (14,11), (14,12), (13,12), (13,13)], #경상북도
    [(15,8), (17,8), (17,10), (16,10), (16,11), (14,11)], #대구
    [(17,9), (18,9), (18,8), (19,8), (19,9), (20,9), (20,10), (21,10)], #부산
    [(16,11), (16,13)], #울산
    [(27,5), (27,6), (25,6)],
]

def drawKorea(targetData, blockedMap, cmapname):
    gamma = 0.75

    whitelabelmin = (max(blockedMap[targetData]) - min(blockedMap[targetData])) * 0.25 + \
                    min(blockedMap[targetData])

    datalabel = targetData

    vmin = min(blockedMap[targetData])
    vmax = max(blockedMap[targetData])

    mapdata = blockedMap.pivot_table(index='y', columns='x', values=targetData)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)

    plt.figure(figsize=(9, 11))
    plt.pcolor(masked_mapdata, vmin=vmin, vmax=vmax, cmap=cmapname,
               edgecolor='#aaaaaa', linewidth=0.5)

    # 지역 이름 표시
    for idx, row in blockedMap.iterrows():
        # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다.
        # (중구, 서구)
        if len(row['ID'].split()) == 2:
            dispname = '{}\n{}'.format(row['ID'].split()[0], row['ID'].split()[1])
        elif row['ID'][:2] == '고성':
            dispname = '고성'
        else:
            dispname = row['ID']

        if len(dispname.splitlines()[-1]) >= 3:
            fontsize, linespacing = 7.5, 1.5
        else:
            fontsize, linespacing = 8, 1.2

        annocolor = 'white' if row[targetData] > whitelabelmin else 'black'
        plt.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold',
                     fontsize=fontsize, ha='center', va='center', color=annocolor,
                     linespacing=linespacing)

    for path in BORDER_LINES:
        ys, xs = zip(*path)
        plt.plot(xs, ys, c='black', lw=1.5)

    plt.gca().invert_yaxis()

    plt.axis('off')

    cb = plt.colorbar(shrink=.1, aspect=10)
    cb.set_label(datalabel)

    plt.tight_layout()
    plt.show()

pop_folium = final_elect_data.set_index('ID')

del pop_folium['광역시도']
del pop_folium['시군']

get_path = 'Data/06. skorea_municipalities_geo_simple.json'
geo_str = json.load(open(get_path, encoding='utf-8'))

map = folium.Map(location=[36.2002, 127.054], zoom_start=6)
map.choropleth(geo_data=geo_str,
               data=pop_folium['moon_vs_hong'],
               columns=[pop_folium.index, pop_folium['moon_vs_hong']],
               fill_color='PuBu',
               key_on='feature.id')

map.save('Data/06. map.html')