import argparse
parser = argparse.ArgumentParser(description='Sentiment analyzer')
parser.add_argument('--proxy', action='store_true', help="use proxy")

args = parser.parse_args()
proxy = args.proxy

print(proxy)