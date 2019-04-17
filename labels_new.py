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
          VALUES ?item {{{0}}} .
          {{?item rdfs:label ?label}}
          UNION 
          {{?item skos:altLabel ?label}} .
          FILTER(LANG(?label) = 'en' || LANG(?label) = 'ru')
        }}""".format(' '.join(["wd:Q" + str(x) for x in range(offset, offset + 300, 1)]))
        results = return_sparql_query_results(sparql_query)
        print(offset)
        offset += 300

        storage = dict()

        for result in results['results']['bindings']:
            if result['item']['value'].startswith('http://www.wikidata.org/entity/'):
                entity = result['item']['value'][31:]
                label = result['label']['value']
                if entity not in storage:
                    storage[entity] = set()

                storage[entity].add(label)

        with codecs.open('labels_new.txt', 'a', "utf-8") as file:
            for entity in storage:
                for label in storage[entity]:
                    file.write(entity + ":" + label + "\n")
            file.flush()

except Exception as e:
    print(offset)
    print(str(e))
