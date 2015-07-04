from bs4 import BeautifulSoup
from clint.textui import puts, colored, progress
import mutagen
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

import requests
import os
import sys
import code
import re
import time

def format(s):
    return s.lower().replace(' ', '_')


def download_file(url, filename):
    print('DOWNLOADING {}'.format(filename))
    r_dl = requests.get(url, stream=True)
    size, count = int(r_dl.headers['content-length']), 0
    while size == 165:
        if count >= 50:
            print('Error downloading file. Please try again.')
            sys.exit()
        r_dl = requests.get(url, stream=True)
        size = int(r_dl.headers['content-length'])
        count += 1
    with open(filename, 'wb') as f:
        for chunk in progress.bar(r_dl.iter_content(chunk_size=1024), expected_size=(size / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()

def print_info(filename):
    mp3file = MP3(filename)
    try:
        meta = EasyID3(filename)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(filename, easy=True)
        meta.add_tags()

    min_sec = time.strftime("%M:%S", time.gmtime(mp3file.info.length))

    bitrate = int(mp3file.info.bitrate/1000)

    basic_info = '{}: {} ({} Mbps)'.format(filename, min_sec, bitrate)
    puts(colored.green(basic_info))

    meta['title'] = meta.get('title') or input('Title: ')
    meta['artist'] = meta.get('artist') or input('Artist: ')
    meta['album'] = meta.get('album') or input('Album: ')
    meta.save()

    title = meta['title'][0] or '[No Title]'
    artist = meta['artist'][0] or '[No Artist]'
    album = meta['album'][0] or '[No Album]'

    id3_info = '\t{}\n\t{} - {}'.format(title, artist, album)

    puts(colored.green(id3_info))

if len(sys.argv) < 2:
    print('Usage: python dl.py [SEARCH TERM]')
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
    size, count = 0.000165, 0
    while size == 0.000165:
        if count >= 30:
            break
        r = requests.head(chosen_link)
        size = int(r.headers['content-length'])/1000000
        count += 1
    puts(colored.cyan('The file is {} MB. Proceed (Y/N)?'.format(size)))
    opt = input('> ')

filename_search = re.search('track/.*/(.*.mp3)', chosen_link)
if filename_search:
    default_name = filename_search.group(1)

puts(colored.cyan('Name your file ({}):'.format(default_name)))

file_name = input('> ')
file_name = file_name or default_name

download_file(chosen_link, file_name)

print_info(file_name)