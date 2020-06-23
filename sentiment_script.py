from finbert.finbert import predict
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
import argparse
import pandas as pd
import time
import argparse
from pathlib import Path
import datetime
import os
import random
import string
import numpy as np
from summa.summarizer import summarize
from sp500project.parse_10k import get_10k
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', -1)  # or 199


parser = argparse.ArgumentParser(description='Sentiment analyzer')
parser.add_argument('--starting_row', type=int, help='Starting row')
parser.add_argument('--ending_row', type=int, help='Ending row')

args = parser.parse_args()
nrows = [args.starting_row,args.ending_row]

cid_10k_500 = pd.read_csv("sp500project/sec_ticker/cid_10k_500.csv", index_col=0)
# cid_500 = cid_500[(cid_500['file']=='10-K')|(cid_500['file']=='10-Q')].iloc[nrows[0]:nrows[1]]
# cid_500 = cid_500[(cid_500['file']=='10-K')].iloc[nrows[0]:nrows[1]]
cid_10k_500 = cid_10k_500[(cid_10k_500['file']=='10-K')].iloc[nrows[0]:nrows[1]]

sentiment = pd.DataFrame(columns=['ticker', 'filing_date', 'link', 'html_link', 'item1a', 'item7', 'item7a'])

fail_links =[]
for cid_idx, row in cid_10k_500.iterrows():
    ticker, company_Name, Sector, cid, company_name, file, filing_date, text_loc, tml = row

    sec_prefix = "https://www.sec.gov/Archives/"

    link = sec_prefix + text_loc
    html_link = sec_prefix + tml

    results = {'ticker': ticker, 'filing_date': filing_date, 'link': link, 'html_link': html_link}

    # print(html_link)
    dict_items = get_10k(link)

    if isinstance(dict_items, str):
        fail_links.append((ticker, filing_date, html_link, link))

    else:
        # for name, txt in zip(['item1a', 'item7', 'item7a'], [item1a, item7, item7a]):

        if not dict_items:
            sentiment = sentiment.append(results, ignore_index=True)
        else:
            for name, txt in dict_items.items():
                print(name)
                # print(txt)
                model = BertForSequenceClassification.from_pretrained('models/classifier_model/finbert-sentiment',
                                                                      num_labels=3, cache_dir=None)

                sentiment_df = predict(txt,model,write_to_csv=False) # sentiment_df = predict(txt,model,write_to_csv=True,path=output)
                # print(sentiment_df)
                ## sentence could be missing footstop at the end
                # sentiment_df['sentence'] = sentiment_df['sentence'].str[-1]
                # print(f"length of sentence column {len(sentiment_df['sentence'])}")
                full_txt = " ".join(sentiment_df['sentence'])

                # print(sentiment_df['sentence'].str.strip().str[-1])
                # print(f"length of ranked sentences {len(summarize(full_txt, ratio=1.0, split=True, scores=True))}")

                try:
                    w_sentiment = pd.DataFrame(summarize(full_txt, ratio=1.0, scores=True), columns=['sentence', 'w'])

                    # w_sentiment = w_sentiment[w_sentiment['sentence'].str.count(' ') > 1]

                    sentiment_df = sentiment_df.merge(w_sentiment, how='inner', on='sentence')
                    # print(f"merged df shape: {sentiment_df.shape}")
                    sentiment_df['w'] = sentiment_df['w']/ np.sum(sentiment_df['w'])
                    # print(sentiment_df.head(10))
                    results[name] = np.sum(sentiment_df['w'] * sentiment_df['sentiment_score'])
                except Exception as e:
                    print(e)
                    print("summa")
                    print(summarize(full_txt, ratio=1.0, scores=True))
                    results[name] = "required manual"
                    pass

            sentiment = sentiment.append(results, ignore_index=True)
        print(cid_idx)
        # print(sentiment)
        # print(f"time elapsed: {(time.time()-start)/60} mins")

## print links that fail ##

for ticker, filing_date, html_link, _ in fail_links:
    print(ticker)
    print(filing_date)
    print(html_link)


nrows = f"{nrows[0]}_{nrows[1]}"
sentiment.to_csv(f"sp500project/sentiment_10K_nrows{nrows}.csv")
pd.DataFrame(fail_links, columns=['ticker', 'filing_date', 'html_link', 'text_link']).to_csv(f"manual_sentiment/manual_{nrows}.csv")