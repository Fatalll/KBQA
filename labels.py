import codecs

from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import json
import re

results = {1: 1}

offset = 223210000
try:
    while results:
        sparql = SPARQLWrapper("http://localhost:9999/C:/Program%20Files/Git/bigdata/namespace/wdq/sparql")
        sparql.setQuery("""
        SELECT DISTINCT ?item ?label ?alias
        WHERE {{
          VALUES ?item {{{0}}}
          ?item rdfs:label ?label .
          ?item skos:altLabel ?alias .
        }}
        """.format(' '.join(["wd:Q" + str(x) for x in range(offset, offset + 10000, 1)])))
        sparql.addParameter("timeout", "30000")
        sparql.setMethod("POST")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        print(offset)
        offset += 10000

        storage = dict()

        for result in results['results']['bindings']:
            if result['item']['value'].startswith('http://www.wikidata.org/entity/'):
                entity = result['item']['value'][31:]
                label = result['label']['value']
                alias = result['alias']['value']
                if entity not in storage:
                    storage[entity] = set()

                storage[entity].add(label)
                storage[entity].add(alias)

        with codecs.open('labels.txt', 'a', "utf-8") as file:
            for entity in storage:
                for label in storage[entity]:
                    file.write(entity + ":" + label + "\n")
            file.flush()

except Exception as e:
    print(offset)
    print(str(e))
