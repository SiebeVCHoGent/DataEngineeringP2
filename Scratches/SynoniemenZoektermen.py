# synoniemen scrapen van https://www.mijnwoordenboek.nl/synoniem.php?woord={woord}&lang=NL voor een dictionary van woorden


import copy
import requests
from bs4 import BeautifulSoup
from time import sleep

# voorlopig gewoon gehardcode, maar later dynamisch ophalen van db

natuurlijkKapitaal = {
            "gebruik van energiebronnen": ["energiebron", "energie vermindering", "energie reductie",
                                           "energie-intensiteit", "energiegebruik", "energieverbruik"],
            "gebruik van waterbronnen": ["waterverbruik", "waterbron", "wateronttrekking",
                                         "waterafvoer", "watergebruik", "afvalwater", "grondwater"],
            "emissies van broeikasgassen": ["broeikasgas", "CO2", "CO²"],
            "vervuilende uitstoot": ["emissie", "uitstoot", "vervuiling", "zure regen",
                                     "uitstoot", "fijnstof", "fijn stof", "vervuilende stof",
                                     "filtertechniek", "luchtzuiverheid", "zuiveringstechnologie"],
            "milieu-impact": ["impact", "milieu-impact", "impact op het milieu", "milieu impact",
                              "milieu", "mobiliteit", "vervoer", "verplaatsing", "fiets",
                              "auto", "staanplaatsen", "parking", "openbaar vervoer",
                              "klimaatimpact", "impact op het klimaat", "klimaatsverandering",
                              "green deal"],
            "impact op gezondheid en veiligheid": ["gezondheid", "recyclage", "recycleren",
                                                   "biodiversiteit", "afval", "afvalproductie",
                                                   "vervuiling"],
            "verdere eisen over bepaalde onderwerpen": ["klimaat", "klimaatsverandering",
                                                        "klimaatopwarming", "opwarming", "scope"],
            "milieu beleid": ["milieubeleid", "hernieuwbare energie", "verspilling",
                              "milieucriteria", "planeet", "klimaatsbeleid", "milieunormen"],
            "SDGs": ["schoon water en sanitair", "betaalbare en duurzame energie",
                     "duurzame steden en gemeenschappen", "verantwoorde consumptie en productie",
                     "klimaatactie", "leven in het water", "leven op het land"]
        }


#als je van de synoniemen ook nog is de synoniemen wilt, dan maak je niet gebruik van een deepcopy van de dictionary

def get_synoniemen(dictionary):

    if dictionary == None:
        raise ValueError("dictionary is None")
    if dictionary == '':
        raise ValueError("dictionary is empty")


    copydict = copy.deepcopy(dictionary)
    for key, value in dictionary.items():
        for woord in value:
            print("searching " + woord)
            while(True):
                try:
                    response = requests.get(f'https://www.mijnwoordenboek.nl/synoniem.php?woord={woord}&lang=NL'.format(woord=woord))
                    break
                except:
                    print('Error, retrying...')
                    sleep(8)
            soup = BeautifulSoup(response.text, 'html.parser')
            synoniemen = soup.find(text = "Synoniemen van {woord}".format(woord=woord))
            synoniemen = synoniemen.find_next()
            if synoniemen.find('ul') is None:
                for synoniem in synoniemen:
                    if(synoniem.text != '' and synoniem.text != ' ' and synoniem.text != '\n'):
                        print(synoniem.text)
                        copydict[key].append(synoniem.text)
            else:
                pass
            sleep(2)

    return copydict

print(get_synoniemen(natuurlijkKapitaal))
