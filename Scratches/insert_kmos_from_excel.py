import datetime

from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def read_kmos():
    import pandas as pd
    df = pd.read_csv("kmos.csv", sep=",")
    # change nan values to None in df
    df = df.where((pd.notnull(df)), '')
    return df.to_dict(orient="records")



# add kmos with sqlalchemy to database
def add_to_database():
    kmos = read_kmos()

    base = declarative_base()
    engine = create_engine('postgresql://postgres:root@localhost/dataengineering')
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

    Session = sessionmaker(bind=engine)
    session = Session()

    # clear all tables
    session.query(Website).delete()
    session.query(Verslag).delete()
    session.query(Kmo).delete()
    session.query(Gemeente).delete()
    session.query(Sector).delete()
    session.commit()



    gemeentes_in_db = session.query(Gemeente).all()
    sectors_in_db = session.query(Sector).all()

    print(gemeentes_in_db)
    for kmo in kmos[:10]:
        postcode = str(kmo['Postcode'])
        # check if gemeente in gemeentes in db
        if not any(postcode == g.postcode for g in gemeentes_in_db):
            # add gemeente to db
            gemeente_to_add = Gemeente(postcode=postcode, naam=kmo['Gemeente'])
            session.add(gemeente_to_add)
            gemeente_to_add = session.query(Gemeente).filter_by(postcode=postcode).first()
            gemeentes_in_db.append(gemeente_to_add)

        #check if sector in sectors in db
        omschrijving = kmo['omschrijving']
        if not any(omschrijving == s.naam for s in sectors_in_db):
            # add sector to db
            sector_to_add = Sector(naam=omschrijving)
            session.add(sector_to_add)
            sectors_in_db.append(sector_to_add)
        sector_id = session.query(Sector).filter(Sector.naam == omschrijving).first().id

        # add kmo to db
        kmo_to_add = Kmo(ondernemingsnummer=kmo['bvd_id'], naam=kmo['Naam'], email=kmo['email'], telefoonnummer=kmo['Telefoon'], adres=kmo['Adres'], beursgenoteerd=kmo['Beursnotatie'] != 'Niet beursgenoteerd', aantalWerknemers=kmo['werknemers'], postcode=postcode, sector=sector_id, isB2B=('groothandel' in omschrijving.lower()))
        session.add(kmo_to_add)

        # create verslag
        verslag_to_add = Verslag(ondernemingsnummer=kmo['bvd_id'], jaar=datetime.datetime.now().year)
        session.add(verslag_to_add)
        #get verslag id
        verslag_id = session.query(Verslag).filter(Verslag.ondernemingsnummer == kmo['bvd_id']).filter(Verslag.jaar == datetime.datetime.now().year).first().id

        # create website
        website_to_add = Website(verslag=verslag_id, url=kmo['Webadres'])
        session.add(website_to_add)



    # add kmos to db
    session.commit()
    session.close()

add_to_database()
