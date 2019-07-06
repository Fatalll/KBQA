import codecs
import re

from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360, 'maxsize': 25}])
# index = "property_index"
index = "entity_index"


def next_key():
    with codecs.open('labels_new_v3_ms.txt', 'r', "utf-8") as file:
        last_key = None
        data = []
        ll = 0
        for line in file:
            record = line.split(':', 1)
            try:
                if int(record[0][1:]) > ll + 10000:
                    ll = int(record[0][1:])
                    print(record[0])

                if record[0] == last_key:
                    data.append(re.sub('[{}:?!,-_/.\"+()«»\\\\]', '', record[1].lower().rstrip()))
                else:
                    if len(data) > 0:
                        es_dict = {'id': last_key, 'labels': data}
                        op_dict = {
                            "_index": index,
                            "_id": last_key,
                            "_source": es_dict
                        }
                        yield op_dict

                    last_key = record[0]
                    data = [re.sub('[{}:?!,-_/.\"+()«»\\\\]', '', record[1].lower().rstrip())]
            except Exception as e:
                print(record)
                print(str(e))


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
                        "shingle": {
                            "type": "text",
                            "analyzer": "shingle_analyzer"
                        }
                    }
                }
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "shingle_analyzer": {
                        "tokenizer": "standard",
                        "filter": [
                            "custom_shingle"
                        ]
                    }
                },
                "filter": {
                    "custom_shingle": {
                        "type": "shingle",
                        "min_shingle_size": "2",
                        "max_shingle_size": "3"
                    }
                }
            }
        }
    }

    es.indices.delete(index=index)
    es.indices.create(index=index, body=settings)

    for ok, result in parallel_bulk(es, next_key(), queue_size=8, thread_count=8, chunk_size=1000):
        if not ok:
            print(result)

