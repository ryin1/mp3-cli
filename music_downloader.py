from bs4 import BeautifulSoup
from contextlib import closing
from selenium import webdriver # pip install selenium
# from selenium.webdriver.support.ui import WebDriverWait

import requests
import os
import sys


def format(s):
    return s.lower().replace(' ', '_')

query = ' '.join(sys.argv[1:])
print(query)

url = 'http://www.junglevibe.net/tracks/{}.html'.format(format(query))

r = requests.get(url)
html = BeautifulSoup(r.text)
ul = html.find('ul', class_='results')
lis = ul.find_all('li')
options = {}
for i, v in enumerate(lis, 1):
	artist = v.find('a', rel='nofollow').text.strip()
	title = v.find('span', class_='songName').text
	dl_link = v.find('p', class_='downloadButton').get('onclick').replace('location.href=\'', '')
	options[i] = (artist, title, dl_link)

for k, v in options.items():
    print('{}: {}{}'.format(k, v[0], v[1]))

choice = int(input('Enter index of song: '))
# choice = 7
chosen_link = options[i][2]

# To prevent download dialog
profile = webdriver.FirefoxProfile()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', '/tmp')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

browser = webdriver.Firefox(profile)
browser.get(chosen_link)

# browser.find_element_by_id('button button-icon big green colored ').click()
