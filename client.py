import requests
import json

url = 'http://localhost:5000/plot'

query = """
    SELECT (COUNT(?human) AS ?count)
    WHERE {
        ?human wdt:P31 wd:Q5 .
    }
"""

params = {
    'query': query,
    'chart_type': 'bar',
    'endpoint': 'https://query.wikidata.org/sparql',
    'format': 'png'
}

response = requests.post(url, json=params)
#print(response.text)
if params['format'] == 'html':
    with open('output2.html', 'wb') as file:
        #file.write(response.text)
        #file.write(response.text.encode('utf-8', 'ignore').decode('utf-8'))
        file.write(response.text.encode('utf-8'))

elif params['format'] == 'png':
    with open('chart.png', 'wb') as file:
        file.write(response.content)

