import pandas as pd
from sentiment_func import item_sentiment_score
from sp500project.parse_10k import get_10k_edgecase
import requests
import re
from bs4 import BeautifulSoup

df = pd.read_csv("manual_sentiment/manual_100_200.txt", names=['ticker', 'filing_date', 'full_html'], delimiter=",")

cid_500_10k = pd.read_csv("sp500project/sec_ticker/cid_10k_500.csv", index_col=0)
# print(df.head(10))
# print(cid_500_10k.head(10))

df =df.merge(cid_500_10k, how='left', left_on=['ticker', 'filing_date'], right_on=['ticker', 'filing_date'])
# print(df.head(10))
# print(df.columns.tolist())
sec_prefix = "https://www.sec.gov/Archives/"

for index_row, row in df.iterrows():
    ticker, filing_date, full_html, _, _, _, _, _, text_loc, _ = row
    text_link = sec_prefix + text_loc
    print(full_html)
    desired_items = get_10k_edgecase(text_link)
    if desired_items is None:
        r = requests.get(full_html)
        links = BeautifulSoup(r.text, 'html.parser').find_all('a')
        links = [x.get('href') for x in links]
        # for link in links:
         #    print(link.get('href'))
        sec_link = "https://www.sec.gov"
        html_10k_loc = [x for x in links if x.endswith("10-k.htm")][0]
        html_r = requests.get(f"{sec_link}{html_10k_loc}")
        html_soup = BeautifulSoup(html_r.text, 'html.parser')

        # print(html_soup.find_all(re.compile("Item(\s|&#160;|&nbsp;)(1A|1B|2|7A|7|8|9)\.{0,1}")))
        # print(html_soup.find_all("Item&nbsp;1A."))

        tag_li = html_soup.find_all('b')
        regex_item = re.compile(r'(Item)')
        tag_items = [tag for tag in tag_li if re.search(regex_item, tag)]


