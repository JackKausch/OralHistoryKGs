import requests
import pandas as pd

relevant_entities = pd.read_csv("people.csv")
output_rows = []

g = Graph()
g.parse("coauthorship.owl")
headers = {
    "User-Agent": "SATORI-Kausch/0.1 (https://realcharacterlanguage.world; mailto:jack.kausch@gmail.com)"
}

endpoint = "https://query.wikidata.org/sparql"

for i in relevant_entities["Wikidata"]:
    qid = str(i).replace("https://www.wikidata.org/wiki/","")

    sparql_query = f"""
    SELECT DISTINCT ?item ?itemLabel ?link2
    WHERE {{
        ?everythingelse ?link wd:{qid} .
        ?everythingelse ?link2 ?item .
        ?item wdt:P31 wd:Q5.
        SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,en" .
        }}
    }}
    """

    params = {"query": sparql_query, "format": "json"}

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        for result in data["results"]["bindings"]:
            item = result["item"]["value"]
            item_label = result["itemLabel"]["value"]

            output_rows.append({
                "Source": qid,
                "Label": item_label,
                "Target": item
            })

            print(qid, item_label, item)

    except Exception as e:
        print("Error:", qid, e)

output = pd.DataFrame(output_rows).drop_duplicates
output.to_csv("output.csv")

