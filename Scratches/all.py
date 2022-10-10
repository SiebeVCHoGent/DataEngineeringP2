from datetime import datetime
import json
from time import sleep

import pandas as pd
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from OphalenVanNBB import get_values_from_nbb
from WebScraper import scrape_website

try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError as E:
    raise FileNotFoundError(
        E,
        f"\nConfig file not found. Make sure 'config.json' is in the root directory of the project."
    )

def read_kmos():
    df = pd.read_csv("kmos.csv", sep=",")
    #shuffle dataframe
    df = df.sample(frac=1).reset_index(drop=True)
    return df.to_dict(orient="records")

base = declarative_base()
engine = create_engine(
    f'postgresql://{config["postgres"]["username"]}:{config["postgres"]["password"]}@{config["postgres"]["host_name"]}/{config["postgres"]["database"]}'
)
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Kmo(base):
    __table__ = base.metadata.tables['kmo']

class Gemeente(base):
    __table__ = base.metadata.tables['gemeente']

class Sector(base):
    __table__ = base.metadata.tables['sector']

class Verslag(base):
    __table__ = base.metadata.tables['verslag']

class Website(base):
    __table__ = base.metadata.tables['website']

class Jaarverslag(base):
    __table__ = base.metadata.tables['jaarverslag']


Session = sessionmaker(bind=engine)
session = Session()

# clear all tables
session.query(Jaarverslag).delete()
session.query(Website).delete()
session.query(Verslag).delete()
session.query(Kmo).delete()
session.query(Gemeente).delete()
session.query(Sector).delete()
session.commit()

start = datetime.now()

def add_fully_kmo(kmo, get_website_data=False, scrape_nbb=False):
    # get gemeente and add it to database
    postcode = str(kmo['Postcode'])
    gemeente = session.query(Gemeente).filter(Gemeente.postcode == postcode).first()
    if gemeente is None:
        gemeente = Gemeente(naam=kmo['Gemeente'], postcode=postcode)
        session.add(gemeente)

    # get sector and add it to database
    sector = session.query(Sector).filter(Sector.naam == kmo['omschrijving']).first()
    if sector is None:
        sector = Sector(naam=kmo['omschrijving'])
        session.add(sector)

    # get sector_id from db
    sector_id = session.query(Sector).filter(Sector.naam == kmo['omschrijving']).first().id

    # add kmo to database
    kmo_to_add = Kmo(ondernemingsnummer=kmo['bvd_id'], naam=kmo['Naam'], email=kmo['email'],
                     telefoonnummer=kmo['Telefoon'], adres=kmo['Adres'],
                     beursgenoteerd=kmo['Beursnotatie'] != 'Niet beursgenoteerd', aantalWerknemers=kmo['werknemers'],
                     postcode=postcode, sector=sector_id, isB2B=('groothandel' in kmo['omschrijving'].lower()))
    session.add(kmo_to_add)

    if scrape_nbb:
        verslagen = get_values_from_nbb(kmo['bvd_id'])
        for v in verslagen:
            # create verslag
            verslag = Verslag(ondernemingsnummer=kmo['bvd_id'], jaar=v['jaar'])
            session.add(verslag)
            verslag_id = session.query(Verslag).filter(Verslag.ondernemingsnummer == kmo['bvd_id']).filter(Verslag.jaar == v['jaar']).first().id
            jaarverslag = Jaarverslag(verslag=verslag_id, id=v['id'], url=v['url'])
            session.add(jaarverslag)


    # check if verslag with current year exists in db
    verslag = session.query(Verslag).filter(Verslag.ondernemingsnummer == kmo['bvd_id']).filter(Verslag.jaar == datetime.now().year).first()
    if verslag is None:
        verslag = Verslag(ondernemingsnummer=kmo['bvd_id'], jaar=datetime.now().year)
        session.add(verslag)
        verslag = session.query(Verslag).filter(Verslag.ondernemingsnummer == kmo['bvd_id']).filter(
            Verslag.jaar == datetime.now().year).first()

    verslag_id = verslag.id

    # create website
    website_to_add = Website(verslag=verslag_id, url=kmo['Webadres'])

    if get_website_data and kmo['Webadres']:
        # scrape website
        try:
            text = scrape_website('https://' + str(kmo['Webadres']))
            # update text in database in website table
            website_to_add.tekst = text
        except Exception as e:
            print('Exception reading website ' + str(e))
            website_to_add.url = ''

    session.add(website_to_add)
    session.commit()


kmos = read_kmos()
for kmo in kmos[:50]:
    add_fully_kmo(kmo, get_website_data=True, scrape_nbb=True)
    sleep(3)

print(f"TIJD: {(datetime.now() - start).seconds} seconden")