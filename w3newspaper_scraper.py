#!/usr/bin/env python3    

from country_list import countries_for_language
from country_list import available_languages
from bs4 import BeautifulSoup
from queue import Queue
from langdetect import detect
from bs4.element import Comment

from scrapy.linkextractors import LinkExtractor

import country_converter as coco
import requests
import csv
import re
import sys
import tldextract



cc = coco.CountryConverter()
headers = ua = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36'}

lang2country = {}
for item in available_languages():
    if '_' in item:
        splits = item.split('_')
        lang = splits[0]
        country = '_'.join(splits[1:])
        if lang not in lang2country:
            lang2country[lang] = [country]
        else:
            lang2country[lang].append(country)


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def get_w3_urls(lang):
    countries = cc.convert(names=lang2country[lang], to='name_short')
    iso3 = cc.convert(names=lang2country[lang], to='iso3')
    w3urls = set()
    for i, country in enumerate(countries):
        w3urls.add((iso3[i], 'https://w3newspapers.com/' + country.lower().replace(' ', '')))
        w3urls.add((iso3[i], 'https://w3newspapers.com/' + country.lower().replace(' ', '-')))
    return w3urls


fmt = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    # domain...
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
    r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


def validate_url(url):
    return re.match(fmt, url)


def extract_sources(html_string):
    soup = BeautifulSoup(html_string)
    anchors= soup.select('h3 a')
    urls = []
    for anchor in anchors:
        urls.append(anchor['href'])
    urls = list(set(urls))
    urls = list(filter(validate_url, urls))
    return urls


def detect_language(response):
    if 'Content-Language' in response.headers:
        return response.headers['Content-Language'].split('_')[0]

    html_string = response.text
    soup = BeautifulSoup(html_string)
    html_root = soup.findAll('html')[0]

    if 'lang' in html_root:
        return html_root['lang']

    text = text_from_html(html_string)

    if len(re.sub(r'\s+', '', text, flags=re.UNICODE)) > 500:
        return detect(text)

    return None


def extract_name(url):
    ext = tldextract.extract(url)
    return str(ext.domain).replace(' ', '_').replace('-', '_')


def write_source(lang, country, url):
    with open('staging', 'a') as fp:
        writer = csv.writer(fp)
        writer.writerow([lang, extract_name(url), url, 'general', country])
        fp.flush()


def main():
    arg_lang = sys.argv[1]
    w3urls = get_w3_urls(arg_lang)
    sources = set()
    crawled_urls = set()
    crawl_queue = Queue()

    for url in w3urls:
        crawl_queue.put(url)

    while not crawl_queue.empty():
        url = crawl_queue.get()
        crawled_urls.add(url)

        response = requests.get(url[1])
        source_urls = extract_sources(response.text)

        for source_url in source_urls:
            try:
                source_response = requests.get(source_url, headers=headers)
                lang = detect_language(source_response)
            except:
                continue
            if lang == arg_lang:
                print('Found source! ', url[0], source_url)
                write_source(arg_lang, url[0], source_url)

        links = []
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            next_url = link.get('href')
            if next_url.startswith(url) and next_url not in crawled_urls:
                crawl_queue.put([url[0], next_url])

main()
