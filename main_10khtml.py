from sp500project.funcs.parse_10khtml import get_items_score, find10Khtml
from sp500project.funcs.parse_10ktext import get_10k_edgecase
from sp500project.funcs.get_sentiment import item_sentiment_score
import pandas as pd
import argparse
import os
import yaml


parser = argparse.ArgumentParser(description='Sentiment HTML, TEXT 10K analyzer')
parser.add_argument('--starting_row', type=int, help='Starting row')
parser.add_argument('--ending_row', type=int, help='Ending row')
parser.add_argument('--proxy', action='store_true', help="use proxy")

args = parser.parse_args()
nrows = [args.starting_row,args.ending_row]

proxy = args.proxy

with open(r'locations.yml') as file:
    locs = yaml.load(file, Loader=yaml.FullLoader)

manual_loc = f"{locs['manual_input']}manual_{nrows[0]}_{nrows[1]}.csv"

df = pd.read_csv(manual_loc, usecols=['ticker', 'filing_date', 'html_link'], delimiter=",")
cid_500_10k = pd.read_csv(locs['cid_500_10k'], index_col=0)


df =df.merge(cid_500_10k, how='left', left_on=['ticker', 'filing_date'], right_on=['ticker', 'filing_date'])
sec_prefix = "https://www.sec.gov/Archives/"



results = pd.DataFrame(columns=['ticker','filing_date','link','html_link','item1a','item7','item7a'])

for index_row, row in df.iterrows():
    ## Looping through each html, text link to find 10k
    ticker, filing_date, html_index, _, _, _, _, _, text_loc, _ = row
    text_link = sec_prefix + text_loc
    html_index = sec_prefix + html_index
    print(f"html index page: {html_index}")
    html_10k_loc = find10Khtml(html_index, proxy=proxy)
    print(f"html 10k loc: {html_10k_loc}")
    print(f"index row: {index_row}")

    if len(html_10k_loc) >0:
        print(f"raw html link: {html_10k_loc[0]}")
        html_10k_loc = "https://www.sec.gov" + html_10k_loc[0]
        print(f"with sec prefix html link: {html_10k_loc}")
        items_scores = get_items_score(html_10k_loc, proxy=proxy)
    else:
        ## there's no html 10k, use text instead
        print(f"text link:{text_link}")
        desired_items = get_10k_edgecase(text_link, proxy=proxy)
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



nrows = f"{nrows[0]}_{nrows[1]}"
results.to_csv(f"{locs['manual_output']}manual_sentiment_10K_nrows{nrows}.csv")

