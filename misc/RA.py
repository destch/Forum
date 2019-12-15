from datetime import datetime
from bs4 import BeautifulSoup
import requests
import pandas as pd

month = datetime.now().month
year = datetime.now().year
link = 'https://www.residentadvisor.net/news/2019/7'

page = requests.get(link)
soup = BeautifulSoup(page.content, "html.parser")
selection = soup.findAll("div", {"class": "clearfix pb8"})
cols = {'title': [], 'link': [], 'description': []}
for text in selection:
    cols['title'].append(text.find('a').contents[0])
    cols['link'].append('https://www.residentadvisor.net' + text.find('a')['href'])
    cols['description'].append(text.find('div', {"class":"grey"}).contents[0])


df = pd.DataFrame.from_dict(cols)
df['source'] = 'Resident Advisor'

df.to_csv('RA.csv')
