import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from sp500project.tools import dedup
from sp500project.funcs.rotating_proxies import proxy_get

def get_10k(text_link, proxy=False):
    # print(text_link)
    # r = requests.get('https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/0000320193-18-000145.txt')
    r = requests.get(text_link) if not proxy else proxy_get(text_link)
    raw_10k = r.text

    # print(raw_10k)
    # print(text_link)




    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')


    # Create 3 lists with the span idices for each regex

    ### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
    ### First filter will give us document tag start <end> and document tag end's <start>
    ### We will use this to later grab content in between these tags
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]

    ### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
    ### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
    ### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K'
    ### as section names
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]


    document = {}

    # Create a loop to go through each section type and save only the 10-K section in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            document[doc_type] = raw_10k[doc_start:doc_end]


    ## found out that Item section strats with bolded section title
    regex_item = re.compile(r'(font-weight:bold;\">Item(\s|&#160;|&nbsp;)(1A|1B|2|7A|7|8|9)\.{0,1})|'
                            r'(ITEM(\s)(1A|1B|2|7A|7|8|9)\.{1,1})|(A>Item)(\s)(1A|1B|2|7A|7|8|9)\.{1,1}|'
                            r'(>Item\s(1A|1B|2|7A|7|8)\.{1,1})|'
                            r'(>Item\s(1A|1B|2|7A|7|8)\.{0,1}<)|'
                            r'(Item\s{1,3}7\.\s{1,3}Management\'s)|'
                            r'(Item\s{1,2}8\.\s{1,3}Financial Statements and Supplementary Data\.)|'
                            r'(ITEM\s(7|7A|8)\s&#15([01]);\s(MANAGEMENT|FINANCIAL))|'
                            r'(ITEM 8 - FINANCIAL)|'
                            r'(ITEM(\s)(1A|1B|2|7A|7|8|9)\s-\s)|'
                            r'(ITEM(\s|&#160;|&nbsp;)(1A|1B|2|7A|7|8|9))')
    # regex_item = re.compile(r'(font-weight:bold;">Item(\s|&#160;|&nbsp;))')

    ## find item section
    try:
        items_matches = regex_item.finditer(document['10-K'])
        items_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in items_matches])
    except Exception:
        return text_link



    # print("items df")
    # print(items_df)


    desired_items = {}


    if len(list(items_df)) >0:

        items_matches = regex_item.finditer(document['10-K'])
        items_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in items_matches])

        items_df.columns = ['item', 'st', 'ed']
        items_df['item'] = items_df.item.str.lower()

        items_df.replace('font-weight:bold;">', '', regex=True, inplace=True)
        items_df.replace('-', '', regex=True, inplace=True)
        items_df.replace('\>','',regex=True,inplace=True)
        items_df.replace('&#(160|150|151);','',regex=True,inplace=True)
        # items_df.replace('&#150;','',regex=True,inplace=True)
        # items_df.replace('&#151;','',regex=True,inplace=True)
        items_df.replace('&nbsp;', '', regex=True, inplace=True)
        items_df.replace('\.', '', regex=True, inplace=True)
        items_df.replace(' ', '', regex=True, inplace=True)
        items_df.replace('\s', '', regex=True, inplace=True)
        items_df.replace('financial', '', regex=True, inplace=True)
        items_df.replace('management', '', regex=True, inplace=True)
        items_df.replace('\'s', '', regex=True, inplace=True)
        items_df.replace('statementsandsupplementarydata', '', regex=True, inplace=True)
        items_df.replace('^a', '', regex=True, inplace=True)
        items_df.replace('<', '', regex=True, inplace=True)

        # print("before dedup items_df")
        # print(items_df)

        ## deduping based on sum of difference in index/ approx words count
        # between items to distiguish which belongs to table of contents, references and Actual Items

        items_df = dedup(items_df)

        # print("after dedup items_df")
        # print(items_df)


        items_df.set_index('item', inplace=True)

        ##  sort by starting index
        items_df.sort_values(by='st', ascending=True, inplace=True)


        ## Only cases left are getting table of contents, which can simply be deduped
        ## items_df = items_df.drop_duplicates(subset=['item'], keep='last')
        items_df = items_df[~items_df.index.duplicated(keep='last')]


        # print("items df")
        # print(items_df)


        starting_items = ['item1a', 'item7','item7a']
        ending_items = ['item1b', 'item7a','item8']

        fuzzy_match_end = {'item1b':'item2',
                           'item7a':'item8',
                           'item8':'item9'} ## this happens if the ending item cannot be found and the next next item is used as a replacement

        for st, ed in zip(starting_items, ending_items):
            if st in items_df.index:
                try:
                    st_loc = items_df.loc[st, 'st']
                    ed_loc = items_df.loc[ed, 'st'] if ed in items_df.index else items_df.loc[fuzzy_match_end[ed], 'st']
                    ## TODO replace
                    desired_items[st] = BeautifulSoup(document['10-K'][st_loc:ed_loc], 'lxml').get_text("\n\n")
                    # desired_items[st] = 'king is so beautifulful so as julie. every one else this is annoying hopeful more than ten words.'
                    # assert len(desired_items[st].split()) > 10 ## making sure section has more than 10 words
                except Exception as e:
                    print("prob missing items")
                    print(e)
                    desired_items[st] = "missing items"
                    pass
            else:

                pass

    else:
        desired_items = text_link


    return desired_items



def get_10k_edgecase(text_link, proxy=False):
    # r = requests.get('https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/0000320193-18-000145.txt')
    r = requests.get(text_link) if not proxy else proxy_get(text_link)
    raw_10k = r.text



    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')


    # Create 3 lists with the span idices for each regex

    ### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
    ### First filter will give us document tag start <end> and document tag end's <start>
    ### We will use this to later grab content in between these tags
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]

    ### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
    ### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
    ### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K'
    ### as section names
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]


    document = {}

    # Create a loop to go through each section type and save only the 10-K section in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            document[doc_type] = raw_10k[doc_start:doc_end]


    ## found out that Item section strats with bolded section title
    regex_item = re.compile(r'((Item|ITEM)\s7\.\s{0,3}MANAGEMENT\'S)|'
                            r'((Item|ITEM)\s8\.\s{0,3}CONSOLIDATED)|'
                            r'((Item|ITEM)\s7A\.\s{0,3}QUANTITATIVE)|'
                            r'((Item|ITEM)\s1A\.\s{0,3}RISK)')


    ## find item section
    items_matches = regex_item.finditer(document['10-K'])
    items_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in items_matches])


    desired_items = {}
    if len(list(items_df)) >0:

        items_matches = regex_item.finditer(document['10-K'])
        items_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in items_matches])

        items_df.columns = ['item', 'st', 'ed']
        items_df['item'] = items_df.item.str.lower()

        items_df.replace('font-weight:bold;">', '', regex=True, inplace=True)
        items_df.replace('-', '', regex=True, inplace=True)
        items_df.replace('\>','',regex=True,inplace=True)
        items_df.replace('&#(160|150|151);','',regex=True,inplace=True)
        items_df.replace('&nbsp;', '', regex=True, inplace=True)
        items_df.replace('\.', '', regex=True, inplace=True)
        items_df.replace(' ', '', regex=True, inplace=True)
        items_df.replace('\s', '', regex=True, inplace=True)
        items_df.replace('financial', '', regex=True, inplace=True)
        items_df.replace('management', '', regex=True, inplace=True)
        items_df.replace('\'s', '', regex=True, inplace=True)
        items_df.replace('statementsandsupplementarydata', '', regex=True, inplace=True)
        items_df.replace('^a', '', regex=True, inplace=True)
        items_df.replace('<', '', regex=True, inplace=True)
        items_df.replace('consolidated', '', regex=True, inplace=True)
        items_df.replace('quantitative', '', regex=True, inplace=True)
        items_df.replace('risk', '', regex=True, inplace=True)

        # print("before dedup items_df")
        # print(items_df)

        ## deduping based on sum of difference in index/ approx words count
        # between items to distiguish which belongs to table of contents, references and Actual Items

        items_df = dedup(items_df)

        # print("after dedup items_df")
        # print(items_df)


        items_df.set_index('item', inplace=True)

        ##  sort by starting index
        items_df.sort_values(by='st', ascending=True, inplace=True)


        items_df = items_df[~items_df.index.duplicated(keep='first')]



        starting_items = ['item1a', 'item7','item7a']
        ending_items = ['item1b', 'item7a','item8']

        fuzzy_match_end = {'item1b':'item2',
                           'item7a':'item8',
                           'item8':'item9'} ## this happens if the ending item cannot be found and the next next item is used as a replacement

        for st, ed in zip(starting_items, ending_items):
            if st in items_df.index:
                try:
                    st_loc = items_df.loc[st, 'st']
                    ed_loc = items_df.loc[ed, 'st'] if ed in items_df.index else items_df.loc[fuzzy_match_end[ed], 'st']
                    ## TODO replace
                    desired_items[st] = BeautifulSoup(document['10-K'][st_loc:ed_loc], 'lxml').get_text("\n\n")
                    # desired_items[st] = 'king is so beautifulful so as julie. every one else this is annoying hopeful more than ten words.'
                    # assert len(desired_items[st].split()) > 10 ## making sure section has more than 10 words
                except Exception as e:
                    print("prob missing items")
                    print(e)
                    desired_items[st] = "missing items"
                    pass
            else:

                pass
        return desired_items

    else:

        return None


def get_10q(text_link):
    # r = requests.get('https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/0000320193-18-000145.txt')
    r = proxy_get(text_link)
    raw_10q = r.text
    # print(text_link)


    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag prceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')


    # Create 3 lists with the span idices for each regex

    ### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
    ### First filter will give us document tag start <end> and document tag end's <start>
    ### We will use this to later grab content in between these tags
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10q)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10q)]

    ### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
    ### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
    ### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K'
    ### as section names
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10q)]


    document = {}

    # Create a loop to go through each section type and save only the 10-Q section in the dictionary
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-Q':
            document[doc_type] = raw_10q[doc_start:doc_end]


    # Write the regex
    # regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8)\.{0,1})|(ITEM\s(1|1A|1B|7A|7|8)$)|(ITEM\s(1|2|7A|7|8)$)|(ITEM\s(1\.|2\.|7A\.|7\.|8\.))')
    regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|7A|7|8)$)|(ITEM\s(1|2|7A|7|8)$)|(ITEM\s(1A|1B|2|7A|7|8)\.{1,1})|(>Item\s(1A|1B|2|7A|7|8)\.{1,1})')

    regex_item = re.compile(r'(>Item(\s|&#160;|&nbsp;))')
    # regex = re.compile(r'(ITEM\s(1\.|2\.|7A\.|7\.|8\.))')

    # Use finditer to math the regex
    # matches = regex.finditer(document['10-K'])

    # [print(x) for x in matches]

    # Matches
    matches = regex.finditer(document['10-Q'])
    item_matches = regex_item.finditer(document['10-Q'])



    # Create the dataframe
    test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()


    # Get rid of unnesesary charcters from the dataframe
    test_df.replace('&#160;',' ',regex=True,inplace=True)
    test_df.replace('&nbsp;',' ',regex=True,inplace=True)
    test_df.replace(' ','',regex=True,inplace=True)
    test_df.replace('\.','',regex=True,inplace=True)
    test_df.replace('>','',regex=True,inplace=True)

    test_df.replace(r'[\n\s]+', '',regex=True,inplace=True)
    # print(test_df)


    # Drop duplicates
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')

    # Set item as the dataframe index
    pos_dat.set_index('item', inplace=True)

    desired_items = {}

    starting_items = ['item1a', 'item7','item7a']
    ending_items = ['item1b', 'item7a','item8']

    fuzzy_match_end = {'item1b':'item2',
                       'item7a':'item8',
                       'item8':'item9'} ## this happens if the ending item cannot be found and the next next item is used as a replacement

    for st, ed in zip(starting_items, ending_items):
        if st in pos_dat.index:
            st_loc = pos_dat['start'].loc[st]
            ed_loc = pos_dat['start'].loc[ed] if ed in pos_dat.index else pos_dat['start'].loc[fuzzy_match_end[ed]]
            desired_items[st] = BeautifulSoup(document['10-K'][st_loc:ed_loc], 'lxml').get_text("\n\n")
        else:
            pass

    # # print(BeautifulSoup(document['10-K'], 'lxml'))
    #
    # ## some filings don't have item 1a to 1b but just item 1
    #
    #
    # try:
    #     for st, ed in zip(['item1a', 'item7', 'item7a'], ['item1b', 'item7a', 'item8']):
    #         desired_items.append(BeautifulSoup(document['10-K'][pos_dat['start'].loc[st]:pos_dat['start'].loc[ed]], 'lxml').get_text("\n\n"))
    #         # print("appending text")
    #         # print(BeautifulSoup(document['10-K'][pos_dat['start'].loc[st]:pos_dat['start'].loc[ed]], 'lxml').get_text("\n\n"))
    # except:
    #     try:
    #         for st, ed in zip(['item1', 'item7', 'item7a'], ['item2', 'item7a', 'item8']):
    #             desired_items.append(BeautifulSoup(document['10-K'][pos_dat['start'].loc[st]:pos_dat['start'].loc[ed]], 'lxml').get_text("\n\n"))
    #     except Exception as e:
    #         print(e)
    #         pass

    return desired_items