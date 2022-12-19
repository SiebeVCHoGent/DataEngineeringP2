from sqlalchemy import MetaData, create_engine, Table, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, func, select, and_,Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres')
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)

class Kmo(base):
    __table__ = base.metadata.tables['kmo']

class Website(base):
    __table__ = base.metadata.tables['website']

class Verslag(base):
    __table__ = base.metadata.tables['verslag']

class Jaarverslag(base):
    __table__ = base.metadata.tables['jaarverslag']

class Zoekterm(base):
    __table__ = base.metadata.tables['searchterm']

class Woord(base):
    __table__ = base.metadata.tables['woord']

class ZoektermScore(base):
    __table__ = base.metadata.tables['zoektermScores']

Session = sessionmaker(bind=engine)
session = Session()

# get all kmo's
kmos = session.query(Kmo).all()

# get all zoektermen
zoektermen = session.query(Zoekterm).all()


# for each kmo, using the ondernemingsnummer get the corresponding verslag id
for kmo in kmos:
    verslag_id = session.query(Verslag.id).filter(Verslag.ondernemingsnummer == kmo.ondernemingsnummer).first()
    verslag_id = verslag_id[0]

    # get the corresponding jaarverslag id
    jaarverslag_id = session.query(Jaarverslag.id).filter(Jaarverslag.verslag == verslag_id).first()
    jaarverslag_id = jaarverslag_id[0]
    # get the corresponding website id
    website_id = session.query(Website.id).filter(Website.verslag == verslag_id).first()
    website_id = website_id[0]

    # for each zoekterm get the id
    for zoekterm in zoektermen:
        zoekterm_id = zoekterm.id

        WoordenInZoekterm = session.query(Woord.woord).filter(Woord.searchterm == zoekterm_id).all()

        #TODO: if row already exists, continue


        # Calculate the score

        # get the minimum and maximum ts_rank using the functions in the database

        #create a string where every word in woordenzoekeerm is seperated by a |

        woordenString = ' | '.join([woord[0] for woord in WoordenInZoekterm])

        minimum = session.query(func.getmints(woordenString)).first()
        minimum = minimum[0]

        maximum = session.query(func.getmaxts(woordenString)).first()
        maximum = maximum[0]

        minimumjv = session.query(func.getmintsJV(woordenString)).first()
        minimumjv = minimumjv[0]

        maximumjv = session.query(func.getmaxtsJV(woordenString)).first()
        maximumjv = maximumjv[0]

        # get the ts_rank for the website

        ts_rank = session.query(func.ts_rank(Website.tekst_vector, func.to_tsquery('dutch', woordenString))).filter(and_(Website.id == website_id, Website.tekst_vector != None)).first()
        ts_rank = ts_rank[0]

        ts_rankjv = session.query(func.ts_rank(Jaarverslag.tekst_vector, func.to_tsquery('dutch', woordenString))).filter(and_(Jaarverslag.id == jaarverslag_id, Jaarverslag.tekst_vector != None)).first()
        ts_rankjv = ts_rankjv[0]


        normalizedRank = (ts_rank - float(minimum)) / (float(maximum) - float(minimum))
        normalizedRankjv = (ts_rankjv - float(minimumjv)) / (float(maximumjv) - float(minimumjv))

        #insert zoektermScore in database using website id, normalizedRank, normalizedRankjv, zoekterm_id, jaarverslag_id

        zoektermScore = ZoektermScore(id = 1, website = website_id, zoekterm = zoekterm_id, jaarverslag = jaarverslag_id, ts_rank = normalizedRank, ts_rankjv = normalizedRankjv)
        
        session.add(zoektermScore)
        session.flush()
        session.commit()

        # close connection

conn.close()
        