from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

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

# get all seachterms
zoektermen = session.query(Zoekterm).all()
verslagen = session.query(Verslag.id).all()


def get_woorden_of_zoekterm(zoekterm_id):
    WoordenInZoekterm = session.query(Woord.woord).filter(Woord.searchterm == zoekterm_id).all()
    return WoordenInZoekterm


def format_woorden(woorden):
    # replace spaces with <-> operator
    return [woord[0].replace(' ', '<->') for woord in woorden]


def score_verslag(woorden):
    # build woorden query
    wq = "to_tsquery('dutch', '{}')".format(' | '.join(woorden))

    scores = session.execute(f"SELECT v.id, ts_rank(jv.tekst_vector, {wq}), "
                           f"ts_rank(w.tekst_vector, {wq}) FROM verslag AS v "
                           "JOIN jaarverslag AS jv ON jv.verslag = v.id "
                           "JOIN website as w ON w.verslag = v.id").all()
    # scores to dataframe
    df = pd.DataFrame(scores, columns=['verslag_id', 'jaarverslag_score', 'website_score'])
    df['jaarverslag_score'] = MinMaxScaler().fit_transform(df['jaarverslag_score'].values.reshape(-1, 1))
    df['website_score'] = MinMaxScaler().fit_transform(df['website_score'].values.reshape(-1, 1))

    return df


def scores_to_db(zoekterm_id, df):
    # insert scores to db
    for index, row in df.iterrows():
        session.add(ZoektermScore(zoekterm_ID=zoekterm_id, jaarverslag_score=row['jaarverslag_score'], website_score=row['website_score']))
    session.commit()

# create timer
import time
start_time = time.time()

if __name__ == '__main__':
    for zoekterm in zoektermen:
        woorden = format_woorden(get_woorden_of_zoekterm(zoekterm.id))
        if len(woorden):
            scores_to_db(zoekterm.id, score_verslag(woorden))

    # end timer
    print("--- %s seconds ---" % (time.time() - start_time))