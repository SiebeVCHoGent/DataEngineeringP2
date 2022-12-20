import pandas as pd

# read nacebel
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

df = pd.read_csv('nacebel.csv', delimiter=';')
# set nan to None
df = df.where((pd.notnull(df)), None)
#drop Nones


# get the level 1 parent
def get_parent(item):
    def get_super(item):
        # get first matching item in dataframe
        #get first item of dataframe
        parent = df[df["Code"] == item].iloc[0]
        if parent["Level"] == 1:
            return parent["Code"]
        return get_super(parent["Parentcode"])

    # check is numer
    if item is not None:
        return get_super(item)
    return item

# apply function on column parentcode

df['test'] = df['Parentcode'].apply(get_parent)
print("Superparent")
print(df.tail(20))

#add to database

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres')
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)


class Sector(base):
    __table__ = base.metadata.tables['sector']
    def __str__(self):
        return str(self.code) + str(self.superparent)

Session = sessionmaker(bind=engine)
session = Session()


# loop over dataframe and add to database
for index, row in df.iterrows():
    found = session.query(Sector).filter(Sector.code == row['Code']).first()
    found.superparent = row['test']
    print(index, found)
session.commit()
