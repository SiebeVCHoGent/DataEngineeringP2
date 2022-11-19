import time

import pandas as pd
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from scraper.nbb import get_verslag_from_nbb, download_verslag
from pdf import read_pdf
from website import scrape_websites

# read banned-domains
with open('data/banned_domains.txt', 'r') as f:
    banned_domains = f.read().splitlines()

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres')
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Kmo(base):
    __table__ = base.metadata.tables['kmo']


class Verslag(base):
    __table__ = base.metadata.tables['verslag']

class Jaarverslag(base):
    __table__ = base.metadata.tables['jaarverslag']

class Website(base):
    __table__ = base.metadata.tables['website']


Session = sessionmaker(bind=engine)
session = Session()


def refactor_csv(df):
    """
    Refactors csv so that the missing data is filled in
    """
    df['omzet'] = df['omzet'].replace('nb', 0)
    df['website'] = df['website'].str.replace('NaN', '')
    df['email'] = df['email'].str.replace('NaN', '')
    df['NACE'] = df['NACE'].replace(1130, None)

    # get all kmos.ondernemingsnummer from database
    kmo_ondernemingsnummers = [kmo.ondernemingsnummer for kmo in session.query(Kmo).all()]
    # filter out kmos that are already in the database
    df = df[~df['ondernemingsnummer'].isin(kmo_ondernemingsnummers)]
    return df


def scrape_kmo(data):
    print(data['ondernemingsnummer'], data['naam'])
    try:
        # get data from nbb
        jaarverslag = get_verslag_from_nbb(data['ondernemingsnummer'], jaar=2021)
        if jaarverslag is not None:
            jaarverslag['tekst'] = read_pdf(download_verslag(jaarverslag['url']))

        verslag = {}
        verslag['jaar'] = jaarverslag['jaar']
        verslag['ondernemingsnummer'] = data['ondernemingsnummer']
        verslag['omzet'] = data['omzet']
        verslag['aantalwerkenemers'] = data['werknemers']
        verslag['balanstotaal'] = data['activa']
        print('\tVERSLAG DONE')

        # get data from website
        website_text = scrape_websites(data['website'], banned_domains, data['naam'], data['gemeente'])
        website = {'url': website_text.split(' ')[1], 'tekst': website_text}
        print('\tWEBSITE DONE')

        # add to database
        kmo = Kmo(ondernemingsnummer=data['ondernemingsnummer'], naam=data['naam'], email=data['email'], telefoonnummer=data['telefoon'], adres=data['adres'], postcode=data['postcode'], beursgenoteerd=data['beursnotatie'], sector=data['NACE'])
        session.add(kmo)

        verslag = Verslag(**verslag)
        session.add(verslag)
        session.flush()
        session.refresh(verslag)
        id = verslag.id

        del jaarverslag['jaar']
        jaarverslag = Jaarverslag(**jaarverslag)
        jaarverslag.verslag = id
        session.add(jaarverslag)

        website = Website(**website)
        website.verslag = id
        session.add(website)
        session.commit()
    except Exception as e:
        print('!! ERROR', str(e))

    time.sleep(5)


if __name__ == '__main__':
    # read from csv
    df = pd.read_csv('data/kmos_3.csv')
    df = refactor_csv(df)
    print(df.info())

    # Start Scraping
    df.apply(scrape_kmo, axis=1)

