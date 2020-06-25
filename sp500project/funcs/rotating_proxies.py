from lxml.html import fromstring
import requests
from itertools import cycle
import traceback

def get_proxies(n_proxies):
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:n_proxies]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


def proxy_get(url, n_proxies=100):
    proxies = get_proxies(n_proxies)
    proxy_pool = cycle(proxies)
    for i in range(1, n_proxies+1):
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        # print("Request #%d" % i)
        try:
            response = requests.get(url, proxies={"http": proxy, "https": proxy})
            return response
        except Exception as e:
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
            pass
    return requests.get(url)

# #If you are copy pasting proxy ips, put in the list below
# #proxies = ['121.129.127.209:80', '124.41.215.238:45169', '185.93.3.123:8080', '194.182.64.67:3128', '106.0.38.174:8080', '163.172.175.210:3128', '13.92.196.150:8080']
# proxies = get_proxies()
# proxy_pool = cycle(proxies)
#
# url = "https://www.sec.gov/Archives/edgar/data/1090872/000104746910010499/a2201423z10-k.htm"
#
# for i in range(1,11):
#     #Get a proxy from the pool
#     proxy = next(proxy_pool)
#     print("Request #%d"%i)
#     try:
#         response = requests.get(url,proxies={"http": proxy, "https": proxy})
#         print(response.json())
#     except Exception as e:
#         #Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
#         #We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
#         print("Skipping. Connnection error")
#         print(e)