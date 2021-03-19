#!/usr/bin/env python3

import csv
import os

from iso639 import languages as iso639langs


fnames = os.listdir('newspapers')

num_sources = {}

for fname in fnames:
    langcode = fname.split('.')[0]

    with open(os.path.join('newspapers', fname)) as fp:
        reader = csv.reader(fp)
        rows = list(reader)
        num_sources[langcode] = len(rows) - 1

langs = num_sources.keys()
name2code = {}
for lang in langs:
    name = iso639langs.get(alpha2=lang).name
    name2code[name] = lang


# generate md
for name in sorted(name2code.keys()):
    print(f'* [{name.capitalize()}](newspapers/{name2code[name]}.csv) - {num_sources[name2code[name]]} sources')
