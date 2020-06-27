from sp500project.tools import dedup
import pandas as pd
from pandas._testing import assert_frame_equal



testing_dfs = ['testing_df', 'testing_df2',
               'testing_df3', 'testing_item78_switched_case',
               'testing_row_bw_df']

for df in testing_dfs:
    test_ans = dedup(pd.read_csv(f"sp500project/testing_dfs/{df}.csv", usecols=['item','st','ed']))
    corr_ans = pd.read_csv(f"sp500project/testing_dfs/correct_dfs/{df}.csv", usecols=['item','st','ed'])
    assert_frame_equal(test_ans.reset_index(drop=True), corr_ans.reset_index(drop=True))
