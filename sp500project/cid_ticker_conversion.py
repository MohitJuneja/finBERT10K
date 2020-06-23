import pandas as pd




cid = pd.read_csv("sec_ticker/sec_ticker.csv", names=['ticker', 'cid'])
cid['ticker'] = cid['ticker'].str.upper()

sp500 = pd.read_csv("sec_ticker/sp500_constituents.csv").rename({'Symbol':'ticker'},axis=1)

print(sp500.merge(cid, how='left', on='ticker'))

master_idx = pd.read_csv("sp500project/sorted_master.tsv", delimiter=)