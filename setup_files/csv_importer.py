import datetime
import os,django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","neuroboun.settings")
django.setup()

import re
from sys import argv
from Bio import Entrez

from neuroextractor.models import Acronym

with open("./BrainRegions.csv") as f:
    content = f.readlines()
print(content[0])

for line in content :
    terms = list(filter(None,re.split(" ?; ?| ?, ?",line.strip().lower())))
    print(terms)
    if len(terms) == 1:
        continue
    Acronym(acronyms=terms).save()
