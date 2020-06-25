from tools import dedup
import pandas as pd


testing2_df = pd.read_csv("sp500project/teting_df2.csv")
testing_df = pd.read_csv("sp500project/testing_df.csv")
print(testing_df)
print(testing2_df)
print(dedup(testing_df))
print(dedup(testing2_df))

## testing with no duplcates item

i, testing3_df = dedup(testing2_df)
print(dedup(testing3_df))