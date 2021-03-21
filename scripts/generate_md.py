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
print(f'# Awesome Newspapers [![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome#readme)')
print(f'> A curated list of online newspapers covering {len(num_sources.keys())} languages and {sum(num_sources.values())} sources.')

print("""

#### Purpose

This list provides newspaper sources which can be useful in building corpora for NLP applications. It is particulary instrumental for low-resource languages which lack large-scale datasets.

#### Support the Work

If you liked the work, or if this project was useful in your work, do consider supporting this project by making a small donation here <a href="https://www.buymeacoffee.com/divkakwani" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="25" width="120"></a>
""")

print('')
print('#### Language-wise Statistics')
print('')

for name in sorted(name2code.keys()):
    print(f'* [{name.capitalize()}](newspapers/{name2code[name]}.csv) - {num_sources[name2code[name]]} sources')
