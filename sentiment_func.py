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
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_colwidth', -1)  # or 199



def item_sentiment_score(txt):
    model = BertForSequenceClassification.from_pretrained('models/classifier_model/finbert-sentiment',
                                                                          num_labels=3, cache_dir=None)
    sentiment_df = predict(txt,model,write_to_csv=False)
    full_txt = " ".join(sentiment_df['sentence'])
    w_sentiment = pd.DataFrame(summarize(full_txt, ratio=1.0, scores=True), columns=['sentence', 'w'])
    sentiment_df = sentiment_df.merge(w_sentiment, how='inner', on='sentence')
    sentiment_df['w'] = sentiment_df['w']/ np.sum(sentiment_df['w'])
    return np.sum(sentiment_df['w'] * sentiment_df['sentiment_score'])


'''
item1a =  open("manual_sentiment/item1a.txt","r").read()
item7 =  open("manual_sentiment/item7.txt","r").read()
item7a =  open("manual_sentiment/item7a.txt","r").read()

print(item_sentiment_score(item7))
print(item_sentiment_score(item7a))

results = {}
for item_text, name in zip([item1a,item7,item7a],['item1a', 'item7','item7a']):
    results[name] = item_sentiment_score(item_text)
print(results)
'''