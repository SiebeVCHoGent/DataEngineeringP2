'''Scrapes the web for info related to a company'''
import re

import requests
import urllib3
from bs4 import BeautifulSoup
from pytesseract import pytesseract
from duckpy import Client
from langdetect import detect

from pdf import read_pdf

pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

urllib3.disable_warnings()

def scrape_google(company_name: str = None,
                  company_city: str = None) -> list[str]:
    '''
    Takes a company name and city and returns a list of related weblinks.
    '''
    if company_name is None or company_city is None or company_name == '' or company_city == '':
        raise ValueError('company_name or company_city is None or empty')

    webquery = '"' + company_name + '"' + ' ' + company_city + ' ' + 'belgie'

    client = Client()

    links = [result.url for result in client.search(webquery, True)[:10]]
    return links


def is_same_domain(url1, url2):
    '''Checks if two urls are from the same domain'''
    if url1 is None or url2 is None:
        return False
    if re.match(r'^(?:http|ftp)s?://', url2) is not None:
        return url1.split('/')[2] == url2.split('/')[2]
    return False


def reformat_link(url, domain):
    '''reformats a link to a full url'''
    if url is None or domain is None or url == '' or domain == '':
        raise ValueError('url or domain is None or empty')

    url = url.split('#')[0]
    url = url.split('?')[0]
    if url != '' and url.startswith('/'):
        return str(domain) + str(url)
    return url


def remove_invalid_links(links, banned_domains):
    '''removes invalid links from a list of links'''

    if links is None or banned_domains is None:
        raise ValueError('links or banned_domains is None')

    cleaned_links = []

    for link in links:
        if str(link) in ('', 'nan'):
            continue
        if link.endswith('/'):
            link = link[:-1]
        if any((link for banned in banned_domains if banned in link)):
            continue
        cleaned_links.append(link)
    return cleaned_links


def scrape_website(url, done: tuple = (), depth=1, banned_domains=None):
    '''
    Scrapes a website for text and links. Calls itself recursively to scrape sublinks.
    '''

    NederlandseText = ''
    EngelseText = ''

    max_depth = 3
    if 'http' not in url:
        url = f'https://{url}'
    if done is None:
        done = (url, )

    if url in done:
        return '','', done

    #recreate tuple done with new url
    done = done + (url, )

    print("requesting " + url)

    html = requests.get(url, timeout=10, verify=False).content
    # check if content is binary pdf
    if html[:4] == b'%PDF':
        text = read_pdf(html)
        try:
            l = detect(text)
        except Exception as e:
            print('!! Error with language detection', str(e))
            return '', '', done
        if(l == 'nl'):
            NederlandseText += text
        elif(l == 'en'):
            EngelseText += text
    else:
        soup = BeautifulSoup(html, 'html.parser')
        text = f" {url} {' '.join(soup.get_text(separator=' ').split())}"
        try:
            l = detect(text)
        except Exception as e:
            print('!! Error with language detection', str(e))
            return '', '', done
            
        if(l == 'nl'):
            NederlandseText += text
        elif(l == 'en'):
            EngelseText += text

    if depth == max_depth or len(done) > 100:
        return str(NederlandseText), str(EngelseText), done

    soup = BeautifulSoup(html, 'html.parser')
    sublinks = soup.find_all('a')

    sublinks = [
        reformat_link(x.get('href'), done[0])
        for x in sublinks if x.get('href')
    ]

    sublinks = [
        sublink for sublink in remove_invalid_links(sublinks, banned_domains)
        if is_same_domain(done[0], sublink)
    ]
    depth += 1

    for sublink in sublinks:
        result1, result2, ddone = scrape_website(sublink, done, depth, banned_domains)
        NederlandseText += result1
        EngelseText += result2
        done = ddone

    #remove NUL (0x00) characters from string and return
    return str(NederlandseText).replace('\x00', ''),str(EngelseText).replace('\x00', ''), done


def scrape_websites(website=None,
                    banned_domains=None,
                    company_name: str = None,
                    company_city: str = None):
    '''
    Takes a website or a company name and city and scrapes duckduckgo for more links.
    Scrapes text from these links.
    '''

    nltxt = ''
    entxt = ''


    done = ()
    try:
        if str(website) not in 'nan':
            nlwebtxt,enwebtxt, done = scrape_website(f"https://{website}", done, 1,
                                                banned_domains)
            nltxt += nlwebtxt
            entxt += enwebtxt
    except Exception as e:
        print('!! Error with own website', str(e))

    links = scrape_google(company_name=company_name, company_city=company_city)
    links.append(website)
    links = remove_invalid_links(links, banned_domains)

    for link in links[:1]:
        nlwebtxt,enwebtxt, done = scrape_website(link, done, 1, banned_domains)
        nltxt += nlwebtxt
        entxt += enwebtxt
    return nltxt,entxt
