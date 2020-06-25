from sp500project.tools import dedup
import pandas as pd


testing_df = pd.read_csv("sp500project/testing_dfs/testing_row_bw_df.csv", usecols=['item', 'st', 'ed'])
print(testing_df)


print(dedup(testing_df))





# exit()
# items = testing_df['item']
# sts = testing_df['st']
# item_order = {"item1a": 0, "item1b": 1, "item2": 2, "item7": 3, "item7a": 4, "item8": 5, "item9": 6}
#
#
# rows_to_drop =[]
# for i, item in enumerate(items):
#     if i > 0 and i < len(items)-1:
#         triplet = [items[i-1], item, items[i+1]]
#
#         if item_order[item] > item_order[items[i-1]] and item_order[item]>item_order[items[i+1]]:
#             # print(f"2nd cond:{i}")
#             if i -1 not in rows_to_drop:
#                 rows_to_drop.append(i)
#
# print(rows_to_drop)
#
# print(dedup(testing_df.drop(rows_to_drop, axis=0)))