from bs4 import BeautifulSoup
from clint.textui import puts, colored, progress

import requests
import os
import sys
import code
import urllib.request
import re


def format(s):
    return s.lower().replace(' ', '_')


def download_file(url, filename):
	print('DOWNLOADING {}'.format(filename))
	r_dl = requests.get(url, stream=True)
	with open(filename, 'wb') as f:
		total_length = int(r_dl.headers['content-length'])
		for chunk in progress.bar(r_dl.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
			if chunk:
				f.write(chunk)
				f.flush()

if len(sys.argv) < 2:
	print('Usage: python3 music_downloader.py [SEARCH TERM]')
	sys.exit()

query = ' '.join(sys.argv[1:])

url = 'http://www.vibeclouds.net/tracks/{}.html'.format(format(query))

r = requests.get(url)
html = BeautifulSoup(r.text)
ul = html.find('ul', class_='results')
lis = ul.find_all('li')
options = {}
for i, v in enumerate(lis, 1):
    artist = v.find('a', rel='nofollow').text.strip()
    title = v.find('span', class_='songName').text
    dl_link = v.find('p', class_='downloadButton').get('onclick').replace('location.href=', '').replace("'", '')
    options[i] = (artist, title, dl_link)

for k, v in options.items():
    puts(colored.green('\t{}: {}{}'.format(k, v[0], v[1])))

opt = 'N'
while opt != 'Y':
	choice = int(input('Enter index of song: '))
	chosen_link = options[choice][2]
	size = 0.000165
	while size == 0.000165:
		r = requests.head(chosen_link)
		size = int(r.headers['content-length'])/1000000
	puts(colored.cyan('The file is {} MB. Proceed (Y/N)?'.format(size)))
	opt = input('> ')

filename_search = re.search('track/.*/(.*.mp3)', chosen_link)
if filename_search:
	default_name = filename_search.group(1)

puts(colored.cyan('Name your file ({}):'.format(default_name)))

file_name = input('> ')
file_name = file_name or default_name

download_file(chosen_link, file_name)