import codecs
from elasticsearch import Elasticsearch
from pymystem3 import Mystem

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 60, 'maxsize': 25}])
m = Mystem()

with codecs.open('dataset.csv', 'r', "utf-8") as file:
    counter = 0
    for line in file:
        record = line.rstrip().split(',', 1)
        test = record[0].lower()
        result = record[1].split(';')

        qq = []
        an = m.analyze(test)
        for a in an:
            if 'analysis' in a and a['analysis']:
                if ["x" for b in ['CONJ', 'INTJ', 'PART', 'PR', 'V', 'SPRO', 'ADV', 'APRO', 'ADVPRO'] if b in a['analysis'][0]['gr']].__len__() == 0:
                    qq.append(a['analysis'][0]['lex'])
            else:
                if a['text'].rstrip():
                    qq.append(a['text'].rstrip())

        # print(qq)
        res = es.search(index='entity_index',  body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": ' '.join(qq),
                                "fields": [
                                    "labels.shingle"
                                ]
                            }
                        }
                    ]
                }
            }
        })

        # print(res)
        flag = False
        for hit in res['hits']['hits']:

            if hit['_source']['id'] in result:
                counter += 1
                flag = True
                # break
                print("Found:", test, hit['_source']['id'], hit['_source']['labels'])

        if not flag:
            print("Not:", test, " ||| ", res['hits']['hits'])
            print(res)
        # else:
        #     print("Ok", test)

print(counter)
