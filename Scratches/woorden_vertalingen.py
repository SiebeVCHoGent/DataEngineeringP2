from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

import googletrans

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres', pool_recycle=300)
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Woord(base):
    __table__ = base.metadata.tables['woord']

    def __str__(self):
        return str(self.id) + ' - ' + str(self.woord)


Session = sessionmaker(bind=engine)
session = Session()

#get woorden
woorden = session.query(Woord).all()

translator = googletrans.Translator()

for i in woorden:
    translation = translator.translate(i.woord, dest='en')
    i.en_woord = translation.text
    print('translated', i.woord, 'to', translation.text)
    session.commit()

