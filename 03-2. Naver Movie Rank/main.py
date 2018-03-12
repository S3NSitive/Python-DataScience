from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

url_base = "http://movie.naver.com/"
url_sub = "/movie/sdb/rank/rmovie.nhn?sel=cur&date=20180311"

page = url_base + url_sub

soup = BeautifulSoup(page, "html.parser")
#print(soup.find_all('div', 'tit5'))
