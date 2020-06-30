from sp500project.funcs.get_sentiment import item_sentiment_score



testing_locs = "sp500project/testing_items/"
loc_1a = 'item1a'
loc_7 = 'item7'
loc_7a = 'item7a'
results = {}
for loc in [loc_1a, loc_7, loc_7a]:
    with open(f"{testing_locs}{loc}.txt", 'r') as file:
        data = file.read().replace('\n', '')
    results[loc] = item_sentiment_score(data)

print(results)