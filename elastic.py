import codecs
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 60, 'maxsize': 25}])


def next_key():
    with codecs.open('labels.txt', 'r', "utf-8") as file:
        last_key = None
        data = []
        ll = 0
        for line in file:
            record = line.split(':', 1)
            if int(record[0][1:]) > ll + 10000:
                ll = int(record[0][1:])
                print(record[0])

            if record[0] == last_key:
                data.append(record[1].lower())
            else:
                if len(data) > 0:
                    es_dict = {'id': last_key, 'labels': data}
                    op_dict = {
                        "_index": 'entity_index',
                        "_id": last_key,
                        "_source": es_dict
                    }
                    yield op_dict

                last_key = record[0]
                data = [record[1].lower()]


if __name__ == '__main__':

    settings = {
        "mappings": {
            "properties": {
                "id": {
                    "type": "text"
                },
                "labels": {
                    "type": "text",
                    "fields": {
                        "ngram": {
                            "type": "text",
                            "analyzer": "entity_analyzer"
                        },
                        "keywords": {
                            "type": "text",
                            "analyzer": "keywords_analyzer"
                        }
                    }
                }
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "entity_analyzer": {
                        "tokenizer": "entity_tokenizer"
                    },
                    "keywords_analyzer": {
                        "tokenizer": "keyword"
                    }
                },
                "tokenizer": {
                    "entity_tokenizer": {
                        "type": "ngram",
                        "min_gram": 3,
                        "max_gram": 3,
                        "token_chars": [
                            "letter",
                            "digit"
                        ]
                    }
                }
            }
        }
    }

    es.indices.delete(index='entity_index')
    es.indices.create(index='entity_index', body=settings)

    for ok, result in parallel_bulk(es, next_key()):
        if not ok:
            print(result)

