import pandas as pd
import numpy as np
def _rank_dedup(df):
    m = df['item'].shift() > df['item']
    dfs = [df for _, df in df.groupby(m.cumsum())]
    item_dedup = [df.drop_duplicates(['item'], keep='first') for df in dfs]
    # print(item_dedup)
    ## get first diff of each unique roe of item
    diff_sum = [(np.sum(df['st'].diff(1)), i) for i, df in enumerate(item_dedup)]
    ## take the df with the largest sum of diff
    take_df = sorted(diff_sum, key=lambda x:x[0])[-1]


    return dfs[take_df[1]]

def dedup(items_df):
    items = items_df['item']
    item_order = {"item1a": 0, "item1b": 1, "item2": 2,
                  "item7": 3, "item7a": 4, "item8": 5,
                  "item9": 6}
    rows_to_drop = []
    for i, item in enumerate(items):
        if i > 0 and i < len(items) - 1:
            if item_order[item] > item_order[items[i - 1]] and item_order[item] > item_order[items[i + 1]]:
                # print(f"2nd cond:{i}")
                if i - 1 not in rows_to_drop:
                    rows_to_drop.append(i)
    return _rank_dedup(items_df.drop(rows_to_drop, axis=0))