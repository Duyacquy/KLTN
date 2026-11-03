import pandas as pd
import tweepy
import math
import json

ACCESS_TOKEN = '1296927624967720968-783mWv2Uo13p4n9OkJmh5VgNkNhabt'
ACCESS_SECRET = 'bXH6AHLHnbilN8j9oSWjSmmvE6FoNIAyC7sSnuQEJ2bKA'
CONSUMER_KEY = 'uJls12lLP4Do2kQ44OtSAeAuD'
CONSUMER_SECRET = 'HObQgM5Cf2g0z1ypBb2wLJVc7hylKHwrRo8iSzPPsrwatjx59J'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

order_list = ["id", "text", "stance", "leaning", "children"]

def recurse(current):
    try:
        status = api.get_status(current['id'], tweet_mode='extended')
        current['text'] = status._json["full_text"]
    except:
        current['text'] = "[DELETED]"

    if current['children'] is not None:
        for i in current['children']:
            recurse(i)
    # print(current)

f = open('test_TEST_TEST.json')
a = json.load(f)

output = open('TEST_TEST_TEXT_ADDED_BACK.json', 'w')
output.write("[")

children = []
current = None

final_id = a[-1]["root_tweet"]["id"]
for i in a:
    print(i)
    root = i["root_tweet"]
    if root["id"] == final_id:
        recurse(root)
        fix_order(root, i, True)
        json.dump(i, output)
        output.write(']')
    else:
        recurse(root)
        fix_order(root, i, True)
        json.dump(i, output)
        output.write(',\n')

output.close()
f.close()


