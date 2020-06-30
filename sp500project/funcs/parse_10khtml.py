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

    ## get html link by finding description is 10K
    # html_10k_loc =  index_content_tbl.loc[index_content_tbl['Description']=='10-K', 'link']
    html_10k_loc = index_content_tbl[(index_content_tbl['Description'].str.contains(r'(10-{0,1}(K|k))') == True) &
                                     (index_content_tbl['Type'].str.contains(r'(10-{0,1}(K|k))') == True)]['link'].values
    html_10k_loc = [x for x in html_10k_loc if x.endswith('.htm')]
    return html_10k_loc


def get_tags(html_link, proxy=False):
    r = requests.get(html_link) if not proxy else proxy_get(html_link)
    # raw_10k = r.text
    html_soup = BeautifulSoup(r.text, 'html.parser')


    ## remove table and img tags

    ## should not take out as some item tags are inside tables
    # [x.extract() for x in html_soup.findAll('table')]
    [x.extract() for x in html_soup.findAll('img')]


    tags_needed = []
    for tag in html_soup.find_all('a'):
        # print(f"a tag: {tag}")
        if 'name' in tag.attrs:
            ## e.g. tags like: item_1a.
            # print(tag.attrs['name'])
            if re.search(r'(item|Item|ITEM)_*\s*(1A|1a|1b|1B|2|7|7A|7a|8)', tag.attrs['name']):
                tags_needed.append(tag)

    ## TODO Need this if "item" not in a tag
    if len(tags_needed)<4:
        tags_needed = []
        for tag in html_soup.find_all('b'):
            # print(tag.get_text())
            if tag.find(string=re.compile(r'(Item|ITEM)\s*(&nbsp;){0,1}(1A|1B|7|7A|8)\.')):
                tags_needed.append(tag)

    if len(tags_needed) < 4:
        tags_needed = []
        for tag in html_soup.find_all('font'):
            if tag.find(string=re.compile(r'(Item|ITEM)\s*(1A|1B|7|7A|8)\.')):
                tags_needed.append(tag)

    return tags_needed


def clean_item_title(tag):
    tag = re.sub(r"\xa0|\n|\s|\.", u"", tag.get_text()).lower()
    return re.sub(r"riskfactors|unresolvedstaffcomments", u"", tag).lower()


def clean_item_name(tag):

    ## return clean item tag for match
    if re.search(r'(item|Item|ITEM)_*\s*(1a)', tag.attrs['name'].lower()):
        return 'item1a'
    elif re.search(r'(item|Item|ITEM)_*\s*(1b)', tag.attrs['name'].lower()):
        return 'item1b'
    elif re.search(r'(item|Item|ITEM)_*\s*(2)', tag.attrs['name'].lower()):
        return 'item2'
    elif re.search(r'(item|Item|ITEM)_*\s*(7a)', tag.attrs['name'].lower()):
        return 'item7a'
    elif re.search(r'(item|Item|ITEM)_*\s*(7)', tag.attrs['name'].lower()):
        return 'item7'
    elif re.search(r'(item|Item|ITEM)_*\s*(8)', tag.attrs['name'].lower()):
        return 'item8'

def tag2cleantag(tag_str):
    ## return clean item tag for match
    if re.search(r'(item|Item|ITEM)_*\s*(1a)', tag_str):
        return 'item1a'
    elif re.search(r'(item|Item|ITEM)_*\s*(1b)', tag_str):
        return 'item1b'
    elif re.search(r'(item|Item|ITEM)_*\s*(2)', tag_str):
        return 'item2'
    elif re.search(r'(item|Item|ITEM)_*\s*(7a)', tag_str):
        return 'item7a'
    elif re.search(r'(item|Item|ITEM)_*\s*(7)', tag_str):
        return 'item7'
    elif re.search(r'(item|Item|ITEM)_*\s*(8)', tag_str):
        return 'item8'




def get_text(start_tag, end_tag):
    li_text = []
    curr_tag = start_tag
    while curr_tag != end_tag:
        if isinstance(curr_tag, Tag):
            li_text.append(re.sub(r"\xa0|\n|\s", u" ", curr_tag.get_text()))

        if curr_tag.next is not None:
            curr_tag = curr_tag.next

        else:
            curr_tag = curr_tag.parent.next_sibling.next_sibling
    return " ".join(list(dict.fromkeys(li_text)))

def get_items_score(html_link, proxy=False):
    tags_needed = get_tags(html_link, proxy=proxy)

    starting_items = ['item1a', 'item7', 'item7a']
    ending_items = ['item1b', 'item7a', 'item8']

    fuzzy_match_end = {'item1b': 'item2',
                       'item7a': 'item8',
                       'item8': 'item9'}  ## this happens if the ending item cannot be found and the next next item is used as a replacement



    # clean_tags = [clean_item_name(tag) for tag in tags_needed]

    if not tags_needed:
        return {}

    ## TODO need to test below
    if 'name' in tags_needed[0].attrs: ## <--need to test this
        ## if tag has attrs name
        # for tag in tags_needed:
            # print(f"attr: {tag}")
        clean_tags = [tag2cleantag(tag.attrs['name'].lower()) for tag in tags_needed]
    else:
        ## if tag has .get_text()
        # for tag in tags_needed:
            # print(f"get txt: {tag}")
        clean_tags = [tag2cleantag(tag.get_text().lower()) for tag in tags_needed]


    # clean_tags = [clean_item_name(tag) for tag in tags_needed]
    print("clean tags")
    print(clean_tags)
    ## don't need to worry duplicates as dict takes last value as key
    clean_tags2tags = dict(zip(clean_tags, tags_needed))

    final_items ={}
    for clean_st_tag, clean_ed_tag in zip(starting_items, ending_items):
        if clean_st_tag in clean_tags:
            try:
                st_tag = clean_tags2tags[clean_st_tag]
                ed_tag = clean_tags2tags[clean_ed_tag] if clean_ed_tag in clean_tags else clean_tags2tags[fuzzy_match_end[clean_ed_tag]]
                full_text = get_text(st_tag, ed_tag)
                final_items[clean_st_tag] = item_sentiment_score(full_text)
            except Exception as e:
                final_items[clean_st_tag] = 'missing end item'
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
