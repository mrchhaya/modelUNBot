from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)
import qwikidata


sparql_query = """
SELECT DISTINCT ?country ?countryLabel ?capital ?capitalLabel ?population ?nominal_GDP ?Human_Development_Index ?currency_symbol_descriptionLabel ?head_of_stateLabel ?area ?flag_image WHERE {
  ?country wdt:P31 wd:Q3624078.
  FILTER(NOT EXISTS { ?country wdt:P31 wd:Q3024240. })
  FILTER(NOT EXISTS { ?country wdt:P31 wd:Q28171280. })
  OPTIONAL { ?country wdt:P36 ?capital. }
  OPTIONAL { ?country wdt:P1082 ?population. }
  OPTIONAL { ?country wdt:P1082 ?population. }
  OPTIONAL { ?country wdt:P2131 ?nominal_GDP. }
  OPTIONAL { ?country wdt:P1081 ?Human_Development_Index. }
  OPTIONAL { ?country wdt:P38 ?currency_symbol_description. }
  OPTIONAL { ?country wdt:P35 ?head_of_state. }
  OPTIONAL {  }
  OPTIONAL { ?country wdt:P2046 ?area. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  OPTIONAL { ?country wdt:P41 ?flag_image. }
}
ORDER BY (?countryLabel)
"""


sq2= """
SELECT ?instance_of ?instance_ofLabel ?shares_border_with ?shares_border_withLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  
  OPTIONAL {  }
  OPTIONAL {  }
  ?instance_of wdt:P31 wd:Q3624078.
  OPTIONAL { ?instance_of wdt:P47 ?shares_border_with. }
}"""

res = return_sparql_query_results(sparql_query)
borderingCountries = return_sparql_query_results(sq2)
# print(res)
# print(res.get('head'))
for i in range(len(borderingCountries.get('results').get('bindings'))):
    print(borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel').value())
    for j in range(len(borderingCountries.get('results').get('bindings')[i].get('instance_ofLabel'))):
        print(borderingCountries.get('results').get('bindings')[i].get('shares_border_withLabel').get('value'))
    # print(borderingCountries.get('results').get('bindings')[i].get('shares_border_withLabel').get('value'))

# for i in range(len(res.get('results').get('bindings'))):
#     try:
#         print("https://upload.wikimedia.org/wikipedia/commons/e/ed/" + res.get('results').get('bindings')[i].get('flag_image').get('value')[51:-1]+'g')
#     except AttributeError:
#         print("FUCKY WUCKY!")
    # print(res.get('results').get('bindings')[i].get('Human_Development_Index').get('value'))

