import io
import re

import requests
import fitz
from PIL.Image import Image
from bs4 import BeautifulSoup
from pytesseract import pytesseract

pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'


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


def remove_invalid_links(links, done):
    banned_patterns = re.compile("(\W*(.svg)\W*)")
    done_set = set(done)
    cleaned_links = []

    #print(done_set)

    for link in links:
        if link.endswith('/'):
            link = link[:-1]
        if not is_same_domain(done[0], link):
            continue
        if link in done_set:
            continue
        if link in ('', 'nan'):
            continue
        if re.match(banned_patterns, link):
            continue
        cleaned_links.append(link)
    return cleaned_links


def scrape_website(url, done=None, depth=1):
    MAX_DEPTH = 3
    if done is None:
        done = list()

    if url in done:
        return ''

    done.append(url if url[-1] != '/' else url[:-1])


    html = requests.get(url, timeout=50).content
    # check if content is binary pdf
    if html[:4] == b'%PDF':
        text = read_pdf(html)
    else:
        soup = BeautifulSoup(html, 'html.parser')
        text = f" {url} {' '.join(soup.get_text(separator=' ').split())}"

    if depth == MAX_DEPTH:
        return str(text)

    sublinks = soup.find_all('a')
    
    sublinks = [
        reformat_link(x.get('href') if x.get('href') else '', done[0])
        for x in sublinks
    ]
    sublinks = remove_invalid_links(sublinks, done)

    for sublink in sublinks:
        text += scrape_website(sublink, done, depth + 1)
        done.append(sublink)
    return text
