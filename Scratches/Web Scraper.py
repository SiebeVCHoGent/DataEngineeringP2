import re

import requests
from bs4 import BeautifulSoup


def is_same_domain(url1, url2):
    if re.match(r'^(?:http|ftp)s?://', url2) is not None:
        return url1.split('/')[2] == url2.split('/')[2]
    return False


def reformat_link(url, domain):
    url = url.split('#')[0]
    url = url.split('?')[0]
    if url != '' and url.startswith('/'):
        return domain + url
    return url


MAX_DEPTH = 3
def scrape_website(url, done=[], depth=1):
    if url in done:
        return ''

    done.append(url if url[-1] != '/' else url[:-1])

    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    text = f" {url} {' '.join(soup.get_text().split())}"

    if depth == MAX_DEPTH:
        return text

    sublinks = soup.find_all('a')
    sublinks = list(map(lambda x: reformat_link(x.get('href') if x.get('href') else '', done[0]), sublinks))

    while len(sublinks):
        sublink = sublinks.pop(0)
        if sublink not in done and is_same_domain(done[0], sublink):
            text += scrape_website(sublink, done, depth+1)
            done.append(sublink)
    return text

text = scrape_website('https://lebb.be')
print(text)