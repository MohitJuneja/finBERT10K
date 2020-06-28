from finbert.finbert import predict
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
import pandas as pd
import numpy as np
from summa.summarizer import summarize



def item_sentiment_score(item_txt):
    if item_txt=="missing items":
        return item_txt

    else:
        item_txt = item_txt.replace('\n', ' ')
        model = BertForSequenceClassification.from_pretrained('models/classifier_model/finbert-sentiment',
                                                                              num_labels=3, cache_dir=None)
        sentiment_df = predict(item_txt,model,write_to_csv=False)

        full_item_txt = " ".join(sentiment_df['sentence'])
        try:
            w_sentiment = pd.DataFrame(summarize(full_item_txt, ratio=1.0, scores=True), columns=['sentence', 'w'])
            sentiment_df = sentiment_df.merge(w_sentiment, how='inner', on='sentence')
            if len(sentiment_df) >1:
                sentiment_df['w'] = sentiment_df['w']/ np.sum(sentiment_df['w'])
                return np.sum(sentiment_df['w'] * sentiment_df['sentiment_score'])
            else:
                ## nothing to join on
                return "join return empty except title row"
        except Exception as e:
            print(e)
            if len(full_item_txt) > 0:
                return "summa won't rank"
            else:
                return "full_text is empty"
            pass
