import pandas as pd
from sentiment_func import item_sentiment_score
from sp500project.parse_10k import get_10k_edgecase
import requests
import re
from bs4 import BeautifulSoup





r = requests.get("https://www.sec.gov/Archives/edgar/data/718877/000104746909002015/a2190811z10-k.htm")


html_soup = BeautifulSoup(r.text, 'html.parser')

tags_needed = []
for tag in html_soup.find_all('b'):
    if tag.find(string=re.compile(r'Item\s{1,6}(1A|1B|7|7A)\.')):
        print(type(tag))
        tags_needed.append(tag)

curr_tag = tags_needed[0]
while curr_tag != tags_needed[1]:
    print(curr_tag)
    print(type(curr_tag))
    curr_tag = curr_tag.next
