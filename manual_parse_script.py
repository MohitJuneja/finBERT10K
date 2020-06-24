from parse_10khtml import get_items_score, find10Khtml
from sp500project.parse_10k import get_10k_edgecase
from sentiment_func import item_sentiment_score
from bs4 import BeautifulSoup
import requests
import pandas as pd
import argparse
import os
import time


parser = argparse.ArgumentParser(description='Sentiment HTML, TEXT 10K analyzer')
parser.add_argument('--starting_row', type=int, help='Starting row')
parser.add_argument('--ending_row', type=int, help='Ending row')

args = parser.parse_args()
nrows = [args.starting_row,args.ending_row]

manual_loc = f"manual_sentiment/manual_{nrows[0]}_{nrows[1]}.txt"
manual_loc = manual_loc if os.path.isfile(manual_loc) else f"{manual_loc[:-4]}.csv"

df = pd.read_csv(manual_loc, usecols=['ticker', 'filing_date', 'html_link'], delimiter=",")
cid_500_10k = pd.read_csv("sp500project/sec_ticker/cid_10k_500.csv", index_col=0)


df =df.merge(cid_500_10k, how='left', left_on=['ticker', 'filing_date'], right_on=['ticker', 'filing_date'])
sec_prefix = "https://www.sec.gov/Archives/"



results = pd.DataFrame(columns=['ticker','filing_date','link','html_link','item1a','item7','item7a'])

for index_row, row in df.iterrows():
    sec_link = "https://www.sec.gov"
    ## Looping through each html, text link to find 10k
    ticker, filing_date, html_index, _, _, _, _, _, text_loc, _ = row
    text_link = sec_prefix + text_loc

    html_10k_loc = find10Khtml(html_index)
    if len(html_10k_loc) >0:
        html_10k_loc = sec_prefix + html_10k_loc
        items_scores = get_items_score(f"{sec_link}{html_10k_loc[0]}")
    else:
        ## there's no html 10k, use text instead
        desired_items = get_10k_edgecase(text_link)
        items_scores = {}
        ## desired_items can return None if no items are found in text, but it should not
        if desired_items is not None:
            for item, item_text in desired_items.items():
                items_scores[item] = item_sentiment_score(item_text)

        ## this mean even for text file we could not find the items
        else:
            items_scores['item1a'] = None
            items_scores['item7'] = None
            items_scores['item7a'] = None
    results = results.append({'ticker': ticker, 'filing_date': filing_date, 'link': text_link, **items_scores},
                             ignore_index=True)
    print(f"finished {index_row}")
    time.sleep(5)


nrows = f"{nrows[0]}_{nrows[1]}"
results.to_csv(f"manual_sentiment/manual_sentiment_10K_nrows{nrows}.csv")

# def find10Khtml(html_index):
#     ## html_index: index page of edgar company's filings
#
#     r = requests.get(html_index)
#
#     index_soup = BeautifulSoup(r.text, 'html.parser')
#
#     ## getting the index table
#     l = []
#     for tr in index_soup.find_all('tr'):
#         td = tr.find_all('td')
#         links = tr.find_all('a')
#         links = [x.get('href') for x in links]
#         row = [tr.contents for tr in td]
#
#         l.append(row + links)
#     index_content_tbl = pd.DataFrame(l, columns=["Seq", "Description", "Document", "Type", "Size", "link"])
#     index_content_tbl["Description"] = index_content_tbl["Description"].str[0]
#
#     ## get html link by finding description is 10K
#     # html_10k_loc =  index_content_tbl.loc[index_content_tbl['Description']=='10-K', 'link']
#     html_10k_loc =  index_content_tbl[index_content_tbl['Description'].str.match(r'(10-{0,1}(K|k))')==True]['link'].values
#     return html_10k_loc
# r = requests.get(html_index)
#
# links = BeautifulSoup(r.text, 'html.parser').find_all('a')
# links = [x.get('href') for x in links]
# sec_link = "https://www.sec.gov"

# html_10k_loc = [x for x in links if x.endswith("10-k.htm")]

## check for if html format is available
# if len(html_10k_loc) >0 :
#     items_scores = get_items_score(f"{sec_link}{html_10k_loc[0]}")
# else:
#     ## there's no html 10k, use text instead
#     desired_items = get_10k_edgecase(text_link)
#     items_scores ={}
#     ## desired_items can return None if no items are found in text, but it should not
#     if desired_items is not None:
#         for item, item_text in desired_items.items():
#             items_scores[item] = item_sentiment_score(item_text)
#     else:
#         items_scores['item1a'] = None
#         items_scores['item7'] = None
#         items_scores['item7a'] = None
#
# results = results.append({'ticker': ticker, 'filing_date': filing_date, 'link': text_link, **items_scores}, ignore_index=True)