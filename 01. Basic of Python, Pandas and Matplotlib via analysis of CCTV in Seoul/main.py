import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import platform
from matplotlib import font_manager, rc
plt.rcParams['axes.unicode_minus'] = False

CCTV_Seoul = pd.read_csv('Data/01. CCTV_in_Seoul.csv', encoding='utf-8')
CCTV_Seoul.rename(columns={CCTV_Seoul.columns[0] : "구별"}, inplace=True)
CCTV_Seoul['최근증가율'] = ((CCTV_Seoul['2016년'] + CCTV_Seoul['2015년'] +
                                    CCTV_Seoul['2014년']) / CCTV_Seoul['2013년도 이전'] * 100)
print(CCTV_Seoul.sort_values(by='최근증가율', ascending=False).head(5))
print()

pop_Seoul = pd.read_excel('Data/01. population_in_Seoul.xls', header = 2,
                          parse_cols = 'B, D, G, J, N', encoding='utf-8')
pop_Seoul.drop([0], inplace=True)
pop_Seoul.drop([26], inplace=True)
pop_Seoul.rename(columns={pop_Seoul.columns[0] : '구별',
                          pop_Seoul.columns[1]: '인구수',
                          pop_Seoul.columns[2]: '한국인',
                          pop_Seoul.columns[3]: '외국인',
                          pop_Seoul.columns[4]: '고령자'}, inplace=True)
pop_Seoul['외국인비율'] = pop_Seoul['외국인'] / pop_Seoul['인구수'] * 100
pop_Seoul['고령자비율'] = pop_Seoul['고령자'] / pop_Seoul['인구수'] * 100
print(pop_Seoul.sort_values(by='인구수', ascending=False).head(5))
print()

data_result = pd.merge(CCTV_Seoul, pop_Seoul, on='구별')
del data_result['2013년도 이전']
del data_result['2014년']
del data_result['2015년']
del data_result['2016년']
data_result.set_index('구별', inplace=True)
print(data_result.head())

print(np.corrcoef(data_result['고령자비율'], data_result['소계']))

if platform.system() == "Darwin":
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    path = "c:\Windows\Fonts\malgun.ttf"
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')
'''
data_result['소계'].sort_values().plot(kind='barh', grid=True, figsize=(10, 8))
data_result['CCTV 비율'] = data_result['소계'] / data_result['인구수'] * 100
data_result['CCTV 비율'].sort_values().plot(kind='barh', grid=True, figsize=(10, 8))
plt.show()
'''
fp1 = np.polyfit(data_result['인구수'], data_result['소계'], 1)
f1 = np.poly1d(fp1)
fx = np.linspace(10000, 700000, 100)

data_result['오차'] = np.abs(data_result['소계'] - f1(data_result['인구수']))

df_sort = data_result.sort_values(by='오차', ascending=False)
df_sort.head()

plt.figure(figsize=(10, 8))
plt.scatter(data_result['인구수'], data_result['소계'], c=data_result['오차'], s=50)
plt.plot(fx, f1(fx), ls='dashed', lw=3, color='g')

for n in range(10):
    plt.text(df_sort['인구수'][n]*1.02, df_sort['소계'][n]*0.98, df_sort.index[n], fontsize=15)

plt.xlabel('인구수')
plt.ylabel('인구당비율')
plt.colorbar()
plt.grid()
plt.show()