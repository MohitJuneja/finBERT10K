from sp500project.funcs.parse_10khtml import get_items_score


# print(get_items_score("https://www.sec.gov/Archives/edgar/data/718877/000104746917001072/a2230993z10-k.htm"))
# print(get_items_score("https://www.sec.gov/Archives/edgar/data/1158449/000115844906000037/aap.htm"))
# print(get_items_score("https://www.sec.gov/Archives/edgar/data/52485/000035254110000009/form10k123109.htm"))
print(get_items_score("https://www.sec.gov/Archives/edgar/data/1037868/000119312516478197/d120829d10k.htm#tx120829_3"))

exit()
# print(get_items_score("https://www.sec.gov/Archives/edgar/data/718877/000104746913001506/a2213119z10-k.htm"))

## unit testing
html_links = ["https://www.sec.gov/Archives/edgar/data/718877/000104746913001506/a2213119z10-k.htm",
              "https://www.sec.gov/Archives/edgar/data/1158449/000115844907000040/aap10k.htm",
              "https://www.sec.gov/Archives/edgar/data/1035443/000103544305000005/are2004_10k.htm",
              "https://www.sec.gov/Archives/edgar/data/1158449/000115844906000037/aap.htm",
              "https://www.sec.gov/Archives/edgar/data/718877/000104746915001298/a2223239z10-k.htm"]

corr_scores = [
    {'item1a': -0.37981266746814646, 'item7': 0.04212746905504747, 'item7a': -0.06678614961198631},
    {'item1a': -0.21706302310875625, 'item7': -0.02478829185855732, 'item7a': 0.06356485716066215},
    {'item7': 0.10525497694319816, 'item7a': -0.07084695824001219},
    {'item1a': -0.13487047206881667, 'item7': 0.03499917991356452, 'item7a': 0.026765227200890473},
    {'item1a': -0.35847130474418254, 'item7': -0.06158143489920158, 'item7a': -0.03145801817897517}
]

for i, (html, corr) in enumerate(zip(html_links, corr_scores)):
    print(i)
    print(get_items_score(html))
    # assert corr == get_items_score(html)
# assert {'item1a': -0.2137492387683114, 'item7': -0.02478829185855732, 'item7a': 0.06356485716066215} == get_items_score("http://sec.gov/Archives/edgar/data/1158449/000115844907000040/aap10k.htm")
# assert {'item1a': -0.2137492387683114, 'item7': -0.02478829185855732, 'item7a': 0.06356485716066215} == get_items_score("https://www.sec.gov/Archives/edgar/data/1158449/000115844907000040/aap10k.htm")
# assert {'item7': 0.10525497694319816, 'item7a': -0.07084695824001219} == get_items_score("https://www.sec.gov/Archives/edgar/data/1035443/000103544305000005/are2004_10k.htm")
# assert {'item1a': -0.13487047206881667, 'item7': 0.03499917991356452, 'item7a': 0.026765227200890473} == get_items_score("https://www.sec.gov/Archives/edgar/data/1158449/000115844906000037/aap.htm")

# assert {'item1a': -0.3575311242188069, 'item7': -0.06158143489920158, 'item7a': -0.03145801817897517} == get_items_score("https://www.sec.gov/Archives/edgar/data/718877/000104746915001298/a2223239z10-k.htm")