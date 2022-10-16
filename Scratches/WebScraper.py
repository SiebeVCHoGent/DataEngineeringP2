import io
import re

import requests
import fitz
from PIL.Image import Image
from bs4 import BeautifulSoup
from pytesseract import pytesseract
import requests
from urllib.parse import urlparse
from typing import List
from requests_html import HTMLSession
from duckpy import Client
from sqlalchemy import true

pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'


def get_source(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)


def scrape_google(company_name: str = None,
                  company_city: str = None) -> List[str]:
    '''
    Takes a company name and city and returns a list of related weblinks.
    '''

    webquery = '"' + company_name + '"' + ' ' + company_city + ' ' + 'belgie'

    client = Client()

    links = [result.url for result in client.search(webquery, True)[:10]]
    #links = ['{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url)) for url in links]
    return links


def read_pdf(content_stream):
    pdf_file = fitz.open(stream=content_stream, filetype="pdf")
    text = ''

    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]

        # Handle Text
        text += page.get_text()

        # Handle Images
        for _, img in enumerate(page.get_images(), start=1):
            # get the XREF of the image
            xref = img[0]

            # Get bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image['image']

            with Image.open(io.BytesIO(image_bytes)) as image:
                # Read Image with OCR
                try:
                    image_text = pytesseract.image_to_string(image)
                    text += f'\n{image_text}'
                except TypeError as TE:
                    print(f'Error in extract_data\n{TE}')
    return str(text)


def is_same_domain(url1, url2):
    if url1 is None or url2 is None:
        return False
    if re.match(r'^(?:http|ftp)s?://', url2) is not None:
        return url1.split('/')[2] == url2.split('/')[2]
    return False


def reformat_link(url, domain):
    if url is None or domain is None:
        raise ValueError('url or domain is None')

    url = url.split('#')[0]
    url = url.split('?')[0]
    if url != '' and url.startswith('/'):
        return str(domain) + str(url)
    return url


def remove_invalid_links(links, banned_domains):
    cleaned_links = []

    for link in links:
        if link in ('', 'nan'):
            continue
        if link.endswith('/'):
            link = link[:-1]
        if any([link for banned in banned_domains if banned in link]):
            continue
        cleaned_links.append(link)
    return cleaned_links


def scrape_website(url, done=None, depth=1, banned_domains=None):
    MAX_DEPTH = 3
    if done is None:
        done = list()

    if 'http' not in url:
        url = f'https://{url}'

    if url in done:
        return '', done

    done.append(url if url[-1] != '/' else url[:-1])

    html = requests.get(url, timeout=50).content
    # check if content is binary pdf
    if html[:4] == b'%PDF':
        text = read_pdf(html)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        text = f" {url} {' '.join(soup.get_text(separator=' ').split())}"

    if depth == MAX_DEPTH:
        return str(text), done

    sublinks = soup.find_all('a')

    sublinks = [
        reformat_link(x.get('href') if x.get('href') else '', done[0])
        for x in sublinks
    ]
    sublinks = [
        sublink for sublink in remove_invalid_links(sublinks, banned_domains)
        if is_same_domain(done[0], sublink)
    ]

    for sublink in sublinks:
        result = scrape_website(sublink, done, depth + 1, banned_domains)
        text += result[0]
        done = result[1]

    #remove NUL (0x00) characters from string and return
    return text.replace('0x00', ''), done


def scrape_websites(website=None,
                    banned_domains=None,
                    company_name: str = None,
                    company_city: str = None):
    text = ''

    done = []

    if str(website) not in 'nan':
        website_text, done = scrape_website(f"https://{website}", None, 1,
                                    banned_domains)
        text += website_text

    links = scrape_google(company_name=company_name, company_city=company_city)
    links.append(website)
    links = remove_invalid_links(links, banned_domains)

    for link in links:
        website_text, done = scrape_website(link, done, 1, banned_domains)
        text += website_text
    return text
