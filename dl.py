from bs4 import BeautifulSoup
from clint.textui import puts, colored, progress
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

import requests
import sys
import re
import time
import mutagen


def format_query(query):
    return query.lower().replace(' ', '_')


def download_file(url, filename):
    print('DOWNLOADING {}'.format(filename))
    r_dl = requests.get(url, stream=True)
    total_size, count = int(r_dl.headers['content-length']), 0
    while total_size == 165:
        if count >= 50:
            print('Error downloading file. Please try again.')
            sys.exit()
        r_dl = requests.get(url, stream=True)
        total_size = int(r_dl.headers['content-length'])
        count += 1
    with open(filename, 'wb') as f:
        for chunk in progress.bar(r_dl.iter_content(chunk_size=1024),
                                  expected_size=(total_size / 1024) + 1):
            if chunk:
                f.write(chunk)
                f.flush()


def print_search(query):
    # Scraping vibeclouds
    url = 'http://www.vibeclouds.net/tracks/{}.html'.format(format_query(query))

    results = requests.get(url)
    html = BeautifulSoup(results.text)
    ul = html.find('ul', class_='results')
    lis = ul.find_all('li')

    if not lis:
        puts(colored.red('\tNo matches found.'))
        sys.exit()

    options = {}
    for i, v in enumerate(lis, 1):
        artist = v.find('a', rel='nofollow').text.strip()
        title = v.find('span', class_='songName').text
        unparsed_link = v.find('p', class_='downloadButton').get('onclick')
        dl_link_search = re.search("location.href='(.*)'", unparsed_link)
        if dl_link_search:
            dl_link = dl_link_search.group(1)
        options[i] = (artist, title, dl_link)


    for k, v in options.items():
        puts(colored.green('\t{}: {}{}'.format(k, v[0], v[1])))
    
    # User-input to choose song
    opt = 'N'
    while opt != 'Y':
        choice = int(input('Enter index of song: '))
        try:
            chosen_link = options[choice][2]
        except KeyError:
            print('Invalid index; try again.')
            continue
        size, count = 0.000165, 0
        while size == 0.000165:
            if count >= 30:
                break
            r = requests.head(chosen_link)
            size = int(r.headers['content-length']) / 1000000
            count += 1
        puts(colored.cyan('The file is {} MB. Proceed? (Y/N) '.format(size)))
        opt = input('> ')

    default_name = re.search('track/.*/(.*.mp3)', chosen_link).group(1)

    puts(colored.cyan('Name your file (default: {}):'.format(default_name)))

    file_name = input('> ')
    file_name = file_name or default_name

    return chosen_link, file_name

def print_info(filename):
    mp3file = MP3(filename)
    try:
        meta = EasyID3(filename)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(filename, easy=True)
        meta.add_tags()

    min_sec = time.strftime("%M:%S", time.gmtime(mp3file.info.length))

    bitrate = int(mp3file.info.bitrate / 1000)

    basic_info = '\t{}: {} ({} Mbps)'.format(filename, min_sec, bitrate)
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

def main():
    if len(sys.argv) < 2:
        print('Usage: python dl.py [SEARCH TERM]')
        sys.exit()

    query = ' '.join(sys.argv[1:])

    chosen_link, file_name = print_search(query)
    download_file(chosen_link, file_name)
    print_info(file_name)

if __name__ == '__main__':
    main()
