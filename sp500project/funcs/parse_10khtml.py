import pandas as pd
import numpy as np
from sp500project.funcs.rotating_proxies import proxy_get
import requests
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from sp500project.funcs.get_sentiment import item_sentiment_score


def find10Khtml(html_index, proxy=False):
    ## html_index: index page of edgar company's filings

    r = requests.get(html_index) if not proxy else proxy_get(html_index)
    index_soup = BeautifulSoup(r.text, 'html.parser')

    ## getting the index table
    l = []
    for tr in index_soup.find_all('tr'):
        td = tr.find_all('td')
        links = tr.find_all('a')
        links = [x.get('href') for x in links]
        row = [tr.contents for tr in td]

        l.append(row + links)
    index_content_tbl = pd.DataFrame(l, columns=["Seq", "Description", "Document", "Type", "Size", "link"])

    index_content_tbl["Description"] = index_content_tbl["Description"].str[0]
    index_content_tbl["Type"] = index_content_tbl["Type"].str[0]
    # print(index_content_tbl)

    ## get html link by finding description is 10K
    # html_10k_loc =  index_content_tbl.loc[index_content_tbl['Description']=='10-K', 'link']
    html_10k_loc = index_content_tbl[(index_content_tbl['Description'].str.contains(r'(10-{0,1}(K|k))') == True) &
                                     (index_content_tbl['Type'].str.contains(r'(10-{0,1}(K|k))') == True)]['link'].values
    html_10k_loc = [x for x in html_10k_loc if x.endswith('.htm')]
    return html_10k_loc


def get_tags(html_link, proxy=False):
    r = requests.get(html_link) if not proxy else proxy_get(html_link)
    html_soup = BeautifulSoup(r.text, 'html.parser')
    tags_needed = []
    for tag in html_soup.find_all('b'):
        if tag.find(string=re.compile(r'(Item|ITEM)\s{1,6}(1A|1B|7|7A|8)\.')):
            tags_needed.append(tag)
    if not tags_needed:
        for tag in html_soup.find_all('font'):
            if tag.find(string=re.compile(r'(Item|ITEM)\s{1,6}(1A|1B|7|7A|8)\.')):
                tags_needed.append(tag)
    return tags_needed


def clean_item_title(tag):
    return re.sub(r"\xa0|\n|\s|\.", u"", re.search(r"(Item|ITEM)\s{1,6}(1A|1B|7|7A|8)\.", tag.get_text()).group(0)).lower()


def get_text(start_tag, end_tag):
    li_text = []
    curr_tag = start_tag
    while curr_tag != end_tag:
        if isinstance(curr_tag, Tag):
            li_text.append(re.sub(r"\xa0|\n|\s", u" ", curr_tag.get_text()))
        curr_tag = curr_tag.next
    return " ".join(list(dict.fromkeys(li_text)))

def get_items_score(html_link, proxy=False):
    tags_needed = get_tags(html_link, proxy=proxy)
    starting_items = ['item1a', 'item7', 'item7a']
    ending_items = ['item1b', 'item7a', 'item8']

    fuzzy_match_end = {'item1b': 'item2',
                       'item7a': 'item8',
                       'item8': 'item9'}  ## this happens if the ending item cannot be found and the next next item is used as a replacement

    clean_tags = [clean_item_title(tag) for tag in tags_needed]

    ## don't need to worry duplicates as dict takes last value as key
    clean_tags2tags = dict(zip(clean_tags, tags_needed))

    final_items ={}
    for clean_st_tag, clean_ed_tag in zip(starting_items, ending_items):
        if clean_st_tag in clean_tags:
            st_tag = clean_tags2tags[clean_st_tag]
            ed_tag = clean_tags2tags[clean_ed_tag] if clean_ed_tag in clean_tags else clean_tags2tags[fuzzy_match_end[clean_ed_tag]]
            full_text = get_text(st_tag, ed_tag)
            final_items[clean_st_tag] = item_sentiment_score(full_text)
        else:
            pass
    return final_items

# html_link = "https://www.sec.gov/Archives/edgar/data/718877/000104746909002015/a2190811z10-k.htm"
# print(get_items_score(html_link))










# exit()
#
# r = requests.get("https://www.sec.gov/Archives/edgar/data/718877/000104746909002015/a2190811z10-k.htm")
#
#
# html_soup = BeautifulSoup(r.text, 'html.parser')
#
# tags_needed = []
# for tag in html_soup.find_all('b'):
#     if tag.find(string=re.compile(r'(Item|ITEM)\s{1,6}(1A|1B|7|7A|8)\.')):
#         tags_needed.append(tag)
#
#
# li_text = []
# curr_tag = tags_needed[0]
# while curr_tag != tags_needed[1]:
#     # print(type(curr_tag))
#     # if isinstance(curr_tag,NavigableString):
#     #     continue
#     if isinstance(curr_tag, Tag):
#         # print(curr_tag.contents)
#         # print("new  tag")
#         # print(curr_tag.get_text())
#         print(type(curr_tag.get_text()))
#         # re.sub(r"</?\[\d+>", "", line)
#         li_text.append(re.sub(r"\xa0|\n|\s", u" ", curr_tag.get_text()))
#     # # print(type(curr_tag))
#     curr_tag = curr_tag.next
# li_text = list(dict.fromkeys(li_text))
# print(li_text)
#
#
