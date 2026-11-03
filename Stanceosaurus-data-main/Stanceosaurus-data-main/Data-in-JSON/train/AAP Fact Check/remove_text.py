import pandas as pd
import json
### MODIFY THESE

def recurse(current):
    removed_value = current.pop('text')
    # current['text'] = ""
    if current['children'] is not None:
        for i in current['children']:
            recurse(i)
    # print(current)

f = open('ethylene_oxide.json')
a = json.load(f)

output = open('test_TEST_TEST.json', 'w')
output.write("[")

children = []
current = None

final_id = a[-1]["root_tweet"]["id"]
for i in a:
    root = i["root_tweet"]
    if root["id"] == final_id:
        recurse(root)
        json.dump(i, output)
        output.write(']')
    else:
        recurse(root)
        json.dump(i, output)
        output.write(',\n')

output.close()
f.close()





