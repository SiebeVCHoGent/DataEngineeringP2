import requests

headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8',
'Cache-Control': 'max-age=0',
'Connection': 'keep-alive',
'Host': 'consult.cbso.nbb.be',
'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': 'Windows',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'none',
'Sec-Fetch-User': '?1',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
}

api_url = 'https://consult.cbso.nbb.be/api/rs-consult/published-deposits?page=0&size=10&enterpriseNumber={}&sort=periodEndDate,desc&sort=depositDate,desc'
url_pdf = 'https://consult.cbso.nbb.be/api/external/broker/public/deposits/pdf/{}'
#link: https://consult.cbso.nbb.be/consult-enterprise


def get_values_from_nbb(id):

    if id is None:
        raise ValueError("id is None")
    if id == "":
        raise ValueError("id is empty")

    # for bedrijf in bedrijven:
    response = requests.get(api_url.format(str(id).upper().replace('BE', '')), headers=headers)
    data = response.json()
    verslagen = []
    for d in data['content']:
        # save id, periodEndDateYear from data
        verslag = {
            'id': d['id'],
            'jaar': d['periodEndDateYear'],
            'url': url_pdf.format(d['id'])
        }
        verslagen.append(verslag)
    return verslagen

