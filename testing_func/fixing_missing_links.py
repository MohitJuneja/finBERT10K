import yaml
import pandas as pd
pd.set_option('display.max_columns', 500)
with open(r'locations.yml') as file:
    locs = yaml.load(file, Loader=yaml.FullLoader)

nrows = [200, 300]
cid_10k_500 = pd.read_csv(locs['cid_500_10k'], index_col=0, usecols=['ticker','cid','filing_date','text','html']).iloc[nrows[0]:nrows[1]]
cid_10k_500.rename({'text':'text_link','html':'html_link'}, axis=1, inplace=True)

file_nrows = f"{nrows[0]}_{nrows[1]}"

sentiment = pd.read_csv(f"{locs['sentiment_output']}/sentiment_10K_nrows{file_nrows}.csv", usecols=['ticker','filing_date'], index_col=0)
sentiment['success'] = True
fail_links = cid_10k_500.merge(sentiment, how='left', left_on=['ticker','filing_date'], right_on=['ticker', 'filing_date'])
fail_links = fail_links[fail_links['success'].isnull()]

fail_links = fail_links.drop('success', axis=1)

# print(fail_links)
## fail_links = pd.DataFrame(columns=['cid', 'ticker', 'filing_date', 'html_link', 'text_link'])



fail_links.to_csv(f"{locs['manual_input']}/manual_{file_nrows}.csv")
