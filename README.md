# mp3-cli
Command line interface for downloading mp3s online conveniently. Runs on Python 3.

# Features
* Search through large music database
* File-size preview before download
* Download progress bar
* ID3 metadata modification

# Dependencies
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* [Clint](https://pypi.python.org/pypi/clint/)
* [Mutagen](https://mutagen.readthedocs.org/en/latest/)
* [Requests](http://docs.python-requests.org/en/latest/)

# Installation
```bash
git clone https://github.com/ryin1/mp3-cli.git
cd mp3-cli
pip3 install -r requirements.txt
```

# Usage
`python3 dl.py [SEARCH TERM]`
