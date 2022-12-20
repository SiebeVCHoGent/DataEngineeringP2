#using sqlalchemy iterate over all the websites in the data base
import time
from sqlalchemy import MetaData, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from website import scrape_website

import pandas as pd

# read banned-domains
with open('banned_domains.txt', 'r') as f:
    banned_domains = f.read().splitlines()

#remove empty lines out of banned_domains
banned_domains = [x for x in banned_domains if x != '']
banned_domains = [x for x in banned_domains if x != ' ']

base = declarative_base()
engine = create_engine('postgresql://postgres:postgres@vichogent.be:40037/postgres', pool_recycle=300)
conn = engine.connect()
metadata = MetaData(engine)
base.metadata.reflect(engine)

class Website(base):
    __table__ = base.metadata.tables['website']
class Verslag(base):
    __table__ = base.metadata.tables['verslag']


Session = sessionmaker(bind=engine)
session = Session()

'''

#er zijn  15000 verslagen
print("geef minbound")
minbound = int(input())
print("geef maxbound")
maxbound = int(input())

# get all verslagen waar het verslag id tussen 1 en 1000 ligt
verslagen = session.query(Verslag).filter(Verslag.id >= minbound).filter(Verslag.id < maxbound).all()

for verslag in verslagen:

    while(True):
        try:
            website = session.query(Website).filter(Website.verslag == verslag.id).first()
            break
        except:
            try:
                conn =  engine.connect()
                website = session.query(Website).filter(Website.verslag == verslag.id).first()
                break
            except:
                #sleep 5 seconds
                time.sleep(5)
                continue

    if(website.nltekst is not None):
        continue
    if(website.entekst is not None):
        continue
    if(website.url in banned_domains):
        print(website.url, 'is banned')
        continue

    print(website.url)

    done = ()
    try:
        if str(website.url) not in 'nan':
            nltxt,entxt, done = scrape_website(website.url, done, 1,
                                                banned_domains)
        print(nltxt)
        print(entxt)

        #save nltxt and entxt to database for this website
        website.nltekst = nltxt
        website.entekst = entxt
        
        while(True):
            try:
                session.commit()
                break
            except:
                try:
                    conn =  engine.connect()
                    session.rollback()
                    break
                except:
                    #sleep 5 seconds
                    time.sleep(5)
                    continue

    except Exception as e:
        print('!! Error with own website', str(e))
        #add website to banned domains txt file on a new line
        with open('data/banned_domains.txt', 'a') as f:
            f.write("\n" + str(website.url))

'''

verslagen = session.query(Verslag).all()

for verslag in verslagen:
    while(True):
        try:
            website = session.query(Website).filter(Website.verslag == verslag.id).first()
            break
        except:
            try:
                conn =  engine.connect()
                website = session.query(Website).filter(Website.verslag == verslag.id).first()
                break
            except:
                #sleep 5 seconds
                time.sleep(5)
                continue

    print("trying to make tsvector for ", website.url)

    if(website.en_vector is not None or website.nl_vector is not None):
        continue

    if(website.nltekst is None):
        #make a tsvector of the entekst and put it in en_vector
        if(website.entekst is not None):
            website.en_vector = func.to_tsvector('english', website.entekst)
    elif (website.nltekst is not None):
        #make a tsvector of the nltekst and put it in nl_vector
        website.nl_vector = func.to_tsvector('dutch', website.nltekst)
    else:
        continue

    print(website.en_vector)
    print(website.nl_vector)
'''
    while(True):
            try:
                session.commit()
                break
            except:
                try:
                    conn =  engine.connect()
                    session.rollback()
                    break
                except:
                    #sleep 5 seconds
                    time.sleep(5)
                    continue
'''
session.close()

