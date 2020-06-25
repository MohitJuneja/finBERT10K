import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


testing_loc = 'output/testing'




## trying to find out the distributions of the sentiments for every line of each items

for item in ['item1a', 'item7', 'item7a']:
    s = pd.read_csv(f"{testing_loc}/{item}.csv")
    s['len_sentence'] = s['sentence'].str.len()

    print(s.describe())
    print(f"equal weights: {s.median()}")
    s = s[s['len_sentence'] >=10]
    sns.jointplot(s['len_sentence'],s['sentiment_score'])
    plt.show()

