import pandas as pd
import numpy as np
def dedup(df):
    m = df['item'].shift() > df['item']
    dfs = [df for _, df in df.groupby(m.cumsum())]
    diff_sum = [(np.sum(df['st'].diff(1)), i) for i, df in enumerate(dfs)]
    take_df = sorted(diff_sum, key=lambda x:x[0])[-1]
    return dfs[take_df[1]]
    # take_df = 0 if all(np.sum(df0['st'].diff(1)) - np.sum(df1['st'].diff(1))) else 1

