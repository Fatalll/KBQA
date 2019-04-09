# coding=utf-8

import json


entities_count = 0
relations_count = 0
full_count = 0

with open("result_final.json", encoding="utf-8") as file, \
        open('stats.json', 'a', encoding='utf8') as outfile, \
        open('full.json', 'a', encoding='utf8') as fullfile:
    for line in file:
        data = json.loads(line)
        entities_count += len(data['entities'])
        relations_count += len(data['relations'])

        if data['entities'] or data['relations']:
            outfile.write(json.dumps(data,
                                     indent=4,
                                     separators=(',', ': '),
                                     ensure_ascii=False) + "\n")

        if data['entities'] and data['relations']:
            full_count += 1
            fullfile.write(json.dumps(data,
                                      indent=4,
                                      separators=(',', ': '),
                                      ensure_ascii=False) + "\n")

print(entities_count, relations_count, full_count)
