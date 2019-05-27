import codecs
import itertools
import re

from elasticsearch import Elasticsearch
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 60, 'maxsize': 25}])
counter = 0

with codecs.open('questions_ms.txt', 'r', "utf-8") as file, codecs.open('questions.txt', 'r', "utf-8") as qfile, codecs.open('questions_ms_t.txt', 'r', "utf-8") as ansfile:
    with codecs.open('q_answers.txt', 'w', "utf-8") as afile:
        for question, answer, questionf, an, qms, ams in itertools.zip_longest(*[file]*2, *[qfile]*2, *[ansfile]*2):
            questionf = re.sub("[{}:?!,_/.\"+()«»\\\\]", '', questionf.strip())
            question = re.sub("[{}:?!,_/.\"+()«»\\\\]", '', question.strip())
            answer = re.sub("[{}:?!,_/.\"+()«»\\\\]", '', ams.strip())

            qq = []
            for word in question.split():
                if ["x" for b in ['CONJ', 'INTJ', 'PART', 'PR', 'V', 'SPRO', 'ADV', 'APRO', 'ADVPRO'] if b in word].__len__() == 0:
                    qq.append(word.split('=', 1)[0].lower())

            print(qq)
            res = es.search(index='entity_index', size=10, body={
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

            q_entities = []
            for hit in res['hits']['hits']:
                q_entities.append(hit['_source']['id'])

            res = es.search(index='entity_index', size=10, body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": answer,
                                    "fields": [
                                        "labels.shingle"
                                    ]
                                }
                            }
                        ]
                    }
                }
            })

            a_entities = []
            for hit in res['hits']['hits']:
                a_entities.append(hit['_source']['id'])

            try:
                sparql_query = """
                SELECT DISTINCT ?entity ?p ?answer
                WHERE {{
                  VALUES ?entity {{ {0} }} .
                  VALUES ?answer {{ {1} {2} }} .
                  ?entity ?p ?value . 
                  OPTIONAL {{ ?value rdfs:label ?label }} .
                  OPTIONAL {{ ?value skos:altLabel ?label }} .
                  FILTER (lcase(str(?value)) = lcase(str(?answer)) || contains(lcase(str(?label)), lcase(str(?answer)))) .
                  FILTER (?p != wikibase:statements && ?p != wikibase:identifiers && ?p != wikibase:sitelinks && ?p != wdt:P1343)
                }}""".format(' '.join(["wd:" + str(x) for x in q_entities]), ' '.join(["wd:" + str(x) for x in a_entities]), '"' + answer + '"')
                results = return_sparql_query_results(sparql_query)

                storage = dict()

                print(questionf, answer)
                for result in results['results']['bindings']:
                    # print(result['item']['value'])
                    print(result)

                afile.write("Question: " + questionf + " | " + " ".join(qq) + "\n")
                afile.write("Question mappings: " + " ".join(q_entities) + "\n")
                afile.write("Answer: " + answer + "\n")
                afile.write("Answer mappings: " + " ".join(a_entities) + "\n")

                if results['results']['bindings']:
                    afile.write("Results:\n")
                    counter += 1
                    for result in results['results']['bindings']:
                        afile.write(result['entity']['value'] + " # " + result['p']['value'] + " # " + result['answer']['value'] + "\n")

                afile.write("\n")
                afile.flush()

            except Exception as e:
                print(str(e))

print(counter)