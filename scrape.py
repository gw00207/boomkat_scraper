"""
Boomkat scraper
February 2019
"""

from requests import get
from bs4 import BeautifulSoup as Soup
import pandas as pd

num_pages = 500
genre = 'All'

pages = []

for i in range(num_pages):
    genres = {'All': '',
              'Basic Channel / Dub Techno': '62',
              'Dark Ambient / Drone / Metal': '57',
              'Early Electronic / Soundtracks': '51',
              'Electronic': '46',
              'Grime / Fwd': '52',
              'Jungle / Footwork': '50',
              'Techno / House': '48'}

    pages.append('https://boomkat.com/new-releases?page=' + str(i+1)
                 + '&q%5Bgenre%5D=' + genres[genre] + '&q%5Bper_page%5D=50')

def get_desc(url: str):
    """get text descriptions from url"""
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Referer': 'https://cssspritegenerator.com',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}

    d = get(url, headers=hdr)
    soup = Soup(d.content, 'html.parser')

    descs = []
    for foo in soup.findAll('div', {'class': 'details'}):
        desc = foo.find('span', {'class': 'text'})
        if desc is None:
            # sometimes desc does not exist
            descs.append(None)
        else:
            # there exists 16 characters of white space and 'more' at the end of each description, we remove these
            descs.append(desc.text.strip()[:-16].replace('\r', ''))

    genres = []
    for foo in soup.findAll('div', {'class': 'table-cell-text-fit'}):
        genre = foo.find('span', {'class': 'genre'})
        if genre is None:
            # sometimes genre does not exist
            genres.append(None)
        else:
            # there exists 20 characters of white space before the genre
            genres.append(genre.text.strip()[20:])

    artists = []
    for foo in soup.findAll('div', {'class': 'table-cell-text-fit'}):
        artist = foo.find('strong')
        if artist is None:
            continue
        else:
            artists.append(artist.text.strip().replace('\r', ''))

    albums = soup.select('span.album-title')
    catalogues = soup.select('span.catnum')

    df = pd.DataFrame()
    df['artist'] = [x for x in artists]
    df['album'] = [x.text.strip() for x in albums]
    df['catalogue_no'] = [x.text.strip()[8:] for x in catalogues]
    # every other row in the genres list is none (not sure why), below adds only the real ones to the dataframe
    df['genre'] = genres[1::2]
    df['description'] = descs
    # TODO walker: add date from div class="large-16 columns header date-header"
    return df

df_list = []
for i in pages:
    df_list.append(get_desc(i))

df = pd.concat(df_list)
print(len(df))
print(df.head())
df.to_csv('data/all.csv', index=False)
