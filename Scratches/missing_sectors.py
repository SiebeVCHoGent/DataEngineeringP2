import pandas
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

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

class Sector(base):
    __table__ = base.metadata.tables['sector']

Session = sessionmaker(bind=engine)
session = Session()


def read_csv():
    return pandas.read_csv('kmos.csv', sep=',')


def get_kmos_from_database_where_sector_is_missing():
    return [e[0] for e in session.query(Kmo.ondernemingsnummer).filter(Kmo.sector == None).all()]


kmos = get_kmos_from_database_where_sector_is_missing()
df = read_csv()

# only keep kmos that are in the database
print(df.info())
df['NACE'] = df["NACE"].astype(str)
df = df[df['ondernemingsnummer'].isin(kmos)]


# for each in df
for index, row in df.iterrows():
    if index < 2:
        break

    ond = row['ondernemingsnummer']
    nace = '0'+ row['NACE']
    print(ond, nace)

    session.query(Kmo).filter(Kmo.ondernemingsnummer == ond).update({Kmo.sector: nace})
    session.commit()