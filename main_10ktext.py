
from finbert.finbert import predict
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
import argparse
import pandas as pd
import argparse
import numpy as np
from summa.summarizer import summarize
from sp500project.funcs.parse_10ktext import get_10k
from sp500project.funcs.get_sentiment import item_sentiment_score

import yaml
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', -1)  # or 199


parser = argparse.ArgumentParser(description='Sentiment analyzer')
parser.add_argument('--starting_row', type=int, help='Starting row')
parser.add_argument('--ending_row', type=int, help='Ending row')
parser.add_argument('--proxy', action='store_true', help="use proxy")


args = parser.parse_args()
nrows = [args.starting_row,args.ending_row]

proxy = args.proxy

with open(r'locations.yml') as file:
    locs = yaml.load(file, Loader=yaml.FullLoader)

cid_10k_500 = pd.read_csv(locs['cid_500_10k'], index_col=0)


cid_10k_500 = cid_10k_500[(cid_10k_500['file']=='10-K')].iloc[nrows[0]:nrows[1]]

sentiment = pd.DataFrame(columns=['ticker', 'filing_date', 'link', 'html_link', 'item1a', 'item7', 'item7a'])

fail_links =[]
for cid_idx, row in cid_10k_500.iterrows():
    ticker, company_Name, Sector, cid, company_name, file, filing_date, text_loc, tml = row

    sec_prefix = "https://www.sec.gov/Archives/"

    text_link = sec_prefix + text_loc
    html_link = sec_prefix + tml

    results = {'ticker': ticker, 'filing_date': filing_date, 'text_link': text_link, 'html_link': html_link}

    dict_items = get_10k(text_link, proxy=proxy)

    print(cid_idx)

    if isinstance(dict_items, str):
        fail_links.append((cid, ticker, filing_date, html_link, text_link))

    elif not dict_items:
        fail_links.append((cid, ticker, filing_date, html_link, text_link))

    else:
        for name, txt in dict_items.items():
            # print(name)
            results[name] = item_sentiment_score(txt)

        sentiment = sentiment.append(results, ignore_index=True)



nrows = f"{nrows[0]}_{nrows[1]}"
sentiment.to_csv(f"{locs['sentiment_output']}/sentiment_10K_nrows{nrows}.csv")
pd.DataFrame(fail_links, columns=['ticker', 'filing_date', 'html_link', 'text_link'])\
    .to_csv(f"{locs['manual_input']}/manual_{nrows}.csv")

# if txt == "missing items":
#     results[name] = txt
# else:
#     model = BertForSequenceClassification.from_pretrained(locs['model'],
#                                                           num_labels=3, cache_dir=None)
#
#     sentiment_df = predict(txt, model,
#                            write_to_csv=False)  # sentiment_df = predict(txt,model,write_to_csv=True,path=output)
#     full_txt = " ".join(sentiment_df['sentence'])
#
#     try:
#         w_sentiment = pd.DataFrame(summarize(full_txt, ratio=1.0, scores=True), columns=['sentence', 'w'])
#
#         sentiment_df = sentiment_df.merge(w_sentiment, how='inner', on='sentence')
#         sentiment_df['w'] = sentiment_df['w'] / np.sum(sentiment_df['w'])
#         results[name] = np.sum(sentiment_df['w'] * sentiment_df['sentiment_score'])
#     except Exception as e:
#         print(e)
#         print("summa")
#         if len(full_txt) > 0:
#             results[name] = "summa won't join"
#         else:
#             results[name] = "full_text is empty"
#         pass