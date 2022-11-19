import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

html = requests.get('https://www.metatopos.eu/belgcombiN.html')
soup = BeautifulSoup(html.text, 'html.parser')
trs = soup.find_all('tr')
a = [{'postcode': tr.find_all('td')[0].text, 'naam': tr.find_all('td')[1].text} for tr in trs[1:]]

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres')
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Gemeente(base):
    __table__ = base.metadata.tables['gemeente']

Session = sessionmaker(bind=engine)
session = Session()

postcodes_done = []
for i in a:
    if str(i['postcode']) not in postcodes_done:
        session.add(Gemeente(postcode=i['postcode'], naam=i['naam']))
        postcodes_done.append(str(i['postcode']))
session.commit()