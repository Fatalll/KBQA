import codecs
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 60, 'maxsize': 25}])

with codecs.open('dataset.csv', 'r', "utf-8") as file:
    counter = 0
    for line in file:
        record = line.rstrip().split(',', 1)
        test = record[0].lower()
        result = record[1].split(';')

        res = es.search(index='entity_index', size=3, body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": test,
                                "fields": [
                                    "labels^5",
                                    "labels.ngram"
                                ]
                            }
                        }
                    ]
                }
            }
        })

        for hit in res['hits']['hits']:
            if hit['_source']['id'] in result:
                counter += 1
                print(test)
                print(hit['_source']['id'], hit['_source']['labels'])

print(counter)
