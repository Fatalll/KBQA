import codecs

from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

results = {1: 1}
offset = 0
try:
    while results:
        sparql_query = """
        SELECT DISTINCT ?item ?label
        WHERE {{
          VALUES ?item {{ {0} }}
          {{?item rdfs:label ?label}}
          UNION 
          {{?item skos:altLabel ?label}} .
          
          ?item wikibase:statements ?pcount .
          
          FILTER(?pcount > 5)
          FILTER(LANG(?label) = 'ru')
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q4167410 }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q1580166 }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q4167836 }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q17633526 }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q13406463 }}
          FILTER NOT EXISTS {{ ?item wdt:P31 wd:Q17329259 }}
        }} ORDER BY ?item """.format(' '.join(["wd:Q" + str(x) for x in range(offset, offset + 300, 1)]))
        results = return_sparql_query_results(sparql_query)
        print(offset)
        offset += 300

        storage = dict()

        for result in results['results']['bindings']:
            # print(result['item']['value'])
            if result['item']['value'].startswith('http://www.wikidata.org/entity/'):
                entity = result['item']['value'][31:]
                label = result['label']['value']
                if entity not in storage:
                    storage[entity] = set()

                storage[entity].add(label)

        with codecs.open('labels_new_v3.txt', 'a', "utf-8") as file:
            for entity in storage:
                for label in storage[entity]:
                    file.write(entity + ":" + label + "\n")
            file.flush()

except Exception as e:
    print(offset)
    print(str(e))
