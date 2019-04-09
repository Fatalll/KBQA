# coding=utf-8

from SPARQLWrapper import SPARQLWrapper, JSON
import pymystem3
import requests
import json
import re

m = pymystem3.Mystem()

relations = dict()

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
SELECT distinct ((SUBSTR(str(?property), 29)) as ?property) ((SUBSTR(str(?equals), 32)) as ?equals) WHERE {{
         ?instance a dbo:Person . 
         ?instance ?property ?obj .
         ?property owl:equivalentProperty ?equals .
         FILTER (SUBSTR(str(?equals), 1, 31) = "http://www.wikidata.org/entity/") .
}}
""")
sparql.addParameter("timeout", "30000")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for z in results['results']['bindings']:
    relations[z['property']['value']] = z['equals']['value']

print(len(relations), relations)
counter = 0

for relation in relations:
    sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
    sparql.setQuery("""
    SELECT ?altLabel WHERE {{
        VALUES (?wd) {{(wd:{0})}}
        ?wd skos:altLabel ?altLabel .
        FILTER (lang(?altLabel) = "ru")
    }}
    """.format(relations[relation]))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    alt_labels = []
    for z in results['results']['bindings']:
        alt_labels.append(z['altLabel']['value'])

    if alt_labels:
        counter += 1

    relations[relation] = alt_labels

# print(counter)

with open("data.tsv", encoding="utf-8") as file:
    for line in file:
        sentence = line.split('\t', 1)[0]
        sentence = sentence.replace('.', ' ')
        sentence = sentence.replace('-', ' ')
        words = sentence.split(' ')

        entities = []
        entity_relations = dict()

        for word in words:
            word_data, word_info = (word + "{").split('{', 1)
            if ',фам' in word_info and '=' in word_info:
                entities.append(word_info.split('=', 1)[0])

            for relation in relations:
                if word_data in relations[relation]:
                    entity_relations[relation] = word_data

        json_object = dict()
        json_object['question'] = sentence
        json_object['entities'] = dict()
        json_object['relations'] = entity_relations

        for entity in entities:
            sparql = SPARQLWrapper("http://localhost:3030/dbpedia/sparql")
            sparql.setQuery("""
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbpedia: <http://dbpedia.org/resource/>
            SELECT ?page ?label ?id WHERE {{
                ?item a dbo:Person .
                ?item dbo:wikiPageID ?id .
                ?item rdfs:label ?label .
                ?item foaf:isPrimaryTopicOf ?page .
                FILTER(regex(replace(lcase(?label),"ё","е"), "\\\\b{0}\\\\b")) .
            }}
            """.format(entity))
            sparql.setReturnFormat(JSON)
            sparql.setTimeout(100)
            results = sparql.query().convert()
            # print(results)

            max_rating = 0
            entity_id = -1
            entity_label = ""
            for z in results['results']['bindings']:
                r = requests.get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/ru.wikipedia/all-access/user/"
                                 + z['label']['value'] + "/monthly/2015010100/2015123100")
                if r.status_code == 200:
                    if max_rating <= r.json()['items'][0]['views']:
                        max_rating = r.json()['items'][0]['views']
                        entity_id = z['id']['value']
                        entity_label = z['label']['value']
                    # print(z['label']['value'], ":", r.json()['items'][0]['views'])

            json_object['entities'][entity] = dict()
            json_object['entities'][entity]['label'] = entity_label
            json_object['entities'][entity]['id'] = entity_id
            json_object['entities'][entity]['relations'] = dict()
            # print(entity_id, max_rating, entity_label)
            # print(sentence)
            # print("Found entity:", entity_label, entity_id)

            for rel in entity_relations:
                sparql = SPARQLWrapper("http://localhost:3030/dbpedia/sparql")
                sparql.setQuery("""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                SELECT ?value WHERE {{
                    ?item dbo:wikiPageID {0} .
                    ?item dbo:{1} ?value .
                }}
                """.format(entity_id, rel))
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                json_object['entities'][entity]['relations'][rel] = []

                for z in results['results']['bindings']:
                    json_object['entities'][entity]['relations'][rel].append(z['value']['value'])
                    print("Result:", z['value']['value'])

        print(json_object)
        with open('result.json', 'a', encoding='utf8') as outfile:
            outfile.write(json.dumps(json_object,
                          indent=4,
                          separators=(',', ': '), ensure_ascii=False) + "\n")

