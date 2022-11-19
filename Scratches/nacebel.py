import pandas as pd
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres')
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Sector(base):
    __table__ = base.metadata.tables['sector']

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    # read from csv
    df = pd.read_csv('nacebel.csv', delimiter=';')
    # replace nan with None
    df = df.where(pd.notnull(df), None)

    # add to sector
    def add_to_db(d):
        s = Sector(code=d['Code'], level=d['Level nr'], naam=d['Label NL'], parent=d['Parent code'])
        session.add(s)


    df.apply(add_to_db, axis=1)
    session.commit()