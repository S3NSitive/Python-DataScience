import warnings
import pandas as pd
import pandas_datareader.data as web
import platform
import numpy as np
import matplotlib.pyplot as plt

from fbprophet import Prophet
from datetime import datetime
from matplotlib import font_manager, rc

warnings.filterwarnings("ignore")

path = 'c:/Windows/Fonts/malgun.ttf'
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')

plt.rcParams['axes.unicode_minus'] = False

pinkwink_web = pd.read_csv('Data/07. PinkWink Web Traffic.csv', encoding='utf-8', thousands=',',
                           names=['data', 'hit'], index_col=0)
pinkwink_web = pinkwink_web[pinkwink_web['hit'].notnull()]

time = np.arange(0, len(pinkwink_web))
traffic = pinkwink_web['hit'].values

fx = np.linspace(0, time[-1], 1000)

def error(f, x, y):
    return np.sqrt(np.mean((f(x)-y)**2))

fp1 = np.polyfit(time, traffic, 1)
f1 = np.poly1d(fp1)

fp2 = np.polyfit(time, traffic, 2)
f2 = np.poly1d(fp2)

fp3 = np.polyfit(time, traffic, 3)
f3 = np.poly1d(fp3)

fp15 = np.polyfit(time, traffic, 15)
f15 = np.poly1d(fp15)
'''
plt.figure(figsize=(10, 6))
plt.scatter(time, traffic, s=10)

plt.plot(fx, f1(fx), lw=4, label='f1')
plt.plot(fx, f2(fx), lw=4, label='f2')
plt.plot(fx, f3(fx), lw=4, label='f3')
plt.plot(fx, f15(fx), lw=4, label='f15')

plt.grid(True, linestyle='-', color='0.75')
plt.legend(loc=2)
plt.show()

df = pd.DataFrame({'ds':pinkwink_web.index, 'y':pinkwink_web['hit']})
df.reset_index(inplace=True)
df['ds'] = pd.to_datetime(df['ds'], format="%y. %m. %d.")
del df['data']

m = Prophet(yearly_seasonality=True)
m.fit(df)
print()
print(df.head(20))
print()
future = m.make_future_dataframe(periods=60)
forecast = m.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())
m.plot(forecast)
plt.show()
'''
df = pd.read_csv('Data/07. example_wp_R.csv')
df['y'] = np.log(df['y'])
df['cap'] = 8.5

m = Prophet(growth='logistic')
m.fit(df)

future = m.make_future_dataframe(periods=1826)
future['cap'] = 8.5
fcst = m.predict(future)

forecast = m.predict(future)
m.plot_components(forecast);
plt.show()