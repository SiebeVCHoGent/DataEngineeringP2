'''Runs the whole data pipeline'''
from datetime import datetime
import json
from itertools import repeat
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, Session
from requests.exceptions import SSLError

from OphalenVanNBB import get_values_from_nbb
from web_scraper import scrape_websites

try:
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
except FileNotFoundError as no_such_file_error:
    raise FileNotFoundError(
        "Config file not found. Make sure 'config.json' is in the root directory of the project."
    ) from no_such_file_error

base = declarative_base()
engine = create_engine(
    f'''postgresql://{config["postgres"]["username"]}:{config["postgres"]["password"]}@{config["postgres"]["host_name"]}/{config["postgres"]["database"]}'''
)

metadata = MetaData(engine)
base.metadata.reflect(engine)


class Kmo(base):
    '''Kmo database class'''
    __table__ = base.metadata.tables['kmo']


class Gemeente(base):
    '''Gemeente database class'''
    __table__ = base.metadata.tables['gemeente']


class Sector(base):
    '''Sector database class'''
    __table__ = base.metadata.tables['sector']


class Verslag(base):
    '''Verslag database class'''
    __table__ = base.metadata.tables['verslag']


class Website(base):
    '''Website database class'''
    __table__ = base.metadata.tables['website']


class Jaarverslag(base):
    '''Jaarverslag database class'''
    __table__ = base.metadata.tables['jaarverslag']


def read_kmos(shuffle=False):
    '''Read kmo's from csv file'''
    data_frame = pd.read_csv("kmos.csv", sep=",")
    # replace omzet with n.b. with None
    data_frame['omzet'] = data_frame['omzet'].replace('n.b.', None)
    # remove all points from omzet and balanstotaal
    #regex=False verwijderd warnings, verandert verder niets
    data_frame['omzet'] = data_frame['omzet'].str.replace(".", "", regex=False)
    data_frame['balanstotaal'] = data_frame['balanstotaal'].str.replace(
        ".", "", regex=False)
    if shuffle:
        #shuffle dataframe
        data_frame = data_frame.sample(frac=1).reset_index(drop=True)
    return data_frame.to_dict(orient="records")


# clear all tables
def clear_tables():
    '''Clear all database tables'''
    session = Session(bind=engine, expire_on_commit=True)
    with session.begin():
        session.query(Jaarverslag).delete()
        session.query(Website).delete()
        session.query(Verslag).delete()
        session.query(Kmo).delete()
        session.query(Gemeente).delete()
        session.query(Sector).delete()
        session.commit()
    session.close()


def add_gemeente(kmo, session, postcode):
    '''Add gemeente to database'''
    try:
        gemeente = session.query(Gemeente).filter(
            Gemeente.postcode == postcode).first()
    except Exception as error:
        print(error)
    if gemeente is None:
        gemeente = Gemeente(naam=kmo['Gemeente'], postcode=postcode)
        session.add(gemeente)


def add_kmo(kmo, session, postcode, sector_id):
    '''Add kmo to database'''
    kmo_to_add = Kmo(
        ondernemingsnummer=kmo['bvd_id'],
        naam=kmo['Naam'],
        email=kmo['email'],
        telefoonnummer=kmo['Telefoon'],
        adres=kmo['Adres'],
        beursgenoteerd=kmo['Beursnotatie'] != 'Niet beursgenoteerd',
        postcode=postcode,
        sector=sector_id,
        isB2B=('groothandel' in kmo['omschrijving'].lower()))
    session.add(kmo_to_add)


def add_verslagen(kmo, session):
    '''Add verslagen to database'''
    verslagen = get_values_from_nbb(kmo['bvd_id'])
    for ver in verslagen:
        # create verslag
        verslag = Verslag(ondernemingsnummer=kmo['bvd_id'], jaar=ver['jaar'])
        session.add(verslag)
        verslag_id = session.query(Verslag).filter(
            Verslag.ondernemingsnummer == kmo['bvd_id']).filter(
                Verslag.jaar == ver['jaar']).first().id
        jaarverslag = Jaarverslag(verslag=verslag_id,
                                  id=ver['id'],
                                  url=ver['url'])
        session.add(jaarverslag)


def get_current_year_verslag(kmo, session):
    '''Check if verslag with current year exists in db'''
    verslag = session.query(Verslag).filter(
        Verslag.ondernemingsnummer == kmo['bvd_id']).filter(
            Verslag.jaar == datetime.now().year).first()
    if verslag is None:
        verslag = Verslag(ondernemingsnummer=kmo['bvd_id'],
                          jaar=datetime.now().year,
                          omzet=kmo['omzet'],
                          balanstotaal=kmo['balanstotaal'],
                          aantalwerkenemers=kmo['werknemers'])
        session.add(verslag)
        verslag = session.query(Verslag).filter(
            Verslag.ondernemingsnummer == kmo['bvd_id']).filter(
                Verslag.jaar == datetime.now().year).first()

    return verslag


def add_website(kmo, get_website_data, banned_domains, session, verslag_id):
    ''' create website'''
    website_to_add = Website(verslag=verslag_id, url=kmo['Webadres'])

    if get_website_data:
        # scrape website
        try:
            # update text in database in website table
            website_to_add.tekst = scrape_websites(str(kmo["Webadres"]),
                                                   banned_domains, kmo["Naam"],
                                                   kmo["Gemeente"])
        except SSLError as ssl_error:
            print(f"Exception reading website {ssl_error}")
            website_to_add.url = ''

    session.add(website_to_add)


def add_sector(kmo, session):
    # get sector and add it to database
    sector = session.query(Sector).filter(
        Sector.naam == kmo['omschrijving']).first()
    if sector is None:
        sector = Sector(naam=kmo['omschrijving'])
        session.add(sector)

        # get sector_id from db
    sector_id = session.query(Sector).filter(
        Sector.naam == kmo['omschrijving']).first().id

    return sector_id


def add_fully_kmo(kmo,
                  get_website_data=False,
                  banned_domains=None,
                  scrape_nbb=False):
    '''Add a full kmo to the database'''
    session = Session(bind=engine, expire_on_commit=True)
    with session.begin():
        # get gemeente and add it to database
        postcode = str(kmo['Postcode'])
        add_gemeente(kmo, session, postcode)

        sector_id = add_sector(kmo, session)

        # add kmo to database
        add_kmo(kmo, session, postcode, sector_id)

        if scrape_nbb:
            add_verslagen(kmo, session)

        verslag = get_current_year_verslag(kmo, session)

        verslag_id = verslag.id

        add_website(kmo, get_website_data, banned_domains, session, verslag_id)
        session.commit()
    session.close()
    print(kmo['Naam'])


def load_banned_domains():
    '''Load banned domains from file'''
    with open('banned_domains.txt', 'r', encoding='utf-8') as bd_file:
        return [domain.removesuffix('\n') for domain in bd_file.readlines()]


def main(multi_threading=True):
    '''Main function'''
    start = datetime.now()
    clear_tables()

    kmos = read_kmos(False)[:16]
    banned_domains = load_banned_domains()

    if multi_threading:
        with ProcessPoolExecutor() as process_pool:
            process_pool.map(add_fully_kmo, kmos, repeat(True),
                             repeat(banned_domains), repeat(True))
    else:
        for kmo in kmos:
            add_fully_kmo(kmo=kmo,
                          get_website_data=True,
                          banned_domains=banned_domains,
                          scrape_nbb=True)

    print(f"TIJD: {(datetime.now() - start).seconds} seconden")


if __name__ == "__main__":
    main(multi_threading=False)
