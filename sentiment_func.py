from finbert.finbert import predict
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
import pandas as pd
import numpy as np
from summa.summarizer import summarize



def item_sentiment_score(txt):
    model = BertForSequenceClassification.from_pretrained('models/classifier_model/finbert-sentiment',
                                                                          num_labels=3, cache_dir=None)
    sentiment_df = predict(txt,model,write_to_csv=False)
    full_txt = " ".join(sentiment_df['sentence'])
    w_sentiment = pd.DataFrame(summarize(full_txt, ratio=1.0, scores=True), columns=['sentence', 'w'])
    sentiment_df = sentiment_df.merge(w_sentiment, how='inner', on='sentence')
    sentiment_df['w'] = sentiment_df['w']/ np.sum(sentiment_df['w'])
    return np.sum(sentiment_df['w'] * sentiment_df['sentiment_score'])

