import pandas as pd
import tweepy
import math
import json

order_list = ["id", "text", "stance", "leaning", "children"]

def recurse(current, previous, root):
    current = {k: current[k] for k in order_list}

    if root:
        previous["root_tweet"] = current
    else:
        previous["children"].append(current)
    if current['children'] is not None:
        for i in current['children']:
            recurse(i)
    # print(current)

f = open('TEST_TEST_TEXT_ADDED_BACK.json')
a = json.load(f)

output = open('TEST_TEST_REORDER.json', 'w')
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


