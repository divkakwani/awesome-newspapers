
import csv
import os


with open('staging') as fp:
    rows = list(csv.reader(fp))
    for row in rows:
        lang, name, url, domain, country = row
        if os.path.exists('newspapers/' + lang + '.csv'):
            data = list(csv.reader(open('newspapers/' + lang + '.csv')))
            header = data[0]
            sources = data[1:]
        else:
            header = ['name', 'homeurl', 'domain', 'country']
            sources = []

        is_there = False
        for source in sources:
            if source[1] == url:
                is_there = True

        if not is_there:
            sources.append([name, url, domain, country])
        sources = sorted(sources, key=lambda s: s[0])

        with open('newspapers/' + lang + '.csv', 'w', newline='') as fp:
            writer = csv.writer(fp)
            writer.writerow(header)
            for source in sources:
                source[0] = source[0].strip()
                source[1] = source[1].strip()
                source[2] = source[2].strip().lower()
                source[3] = source[3].strip().lower()
                writer.writerow(source)

