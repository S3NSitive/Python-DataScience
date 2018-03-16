import pandas as pd
import numpy as np
import time
import platform
import matplotlib.pyplot as plt

from matplotlib import font_manager, rc
from selenium import webdriver

path = 'c:/Windows/Fonts/malgun.ttf'
if platform.system() == 'Darwin':
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
else:
    print('Unknown system')

plt.rcParams['axes.unicode_minus'] = False

driver = webdriver.Chrome('Driver/chromedriver.exe')
driver.get("http://info.nec.go.kr/main/showDocument.xhtml?electionId=0000000000&topMenuId=VC&secondMenuId=VCCP09")

driver.find_element_by_id("electionType1").click()
driver.find_element_by_id("electionName").send_keys("제19대")
time.sleep(1)
driver.find_element_by_id("electionCode").send_keys("대통령선거")

sido_list_raw = driver.find_element_by_xpath('//*[@id="cityCode"]')
sido_list = sido_list_raw.find_elements_by_tag_name("option")
sido_name_values = [option.text for option in sido_list]
sido_name_values = sido_name_values[2:]
print(sido_name_values)
driver.close()
