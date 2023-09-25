from flask import Flask, request
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

@app.route('/human_count', methods=['GET'])
def human_count():
    query_template = """

        SELECT (COUNT(?human) AS ?count)
        WHERE {
            ?human wdt:P31 wd:Q5 .
        }
        
    """
    #min_year = request.args.get('min_year', default=2022, type=int)
    #max_year = request.args.get('max_year', default=2023, type=int)
    query = query_template

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    data = results["results"]["bindings"]
    count = int(data[0]["count"]["value"])

    fig = px.bar(x=["Number of humans"], y=[count], labels={"x": "Count", "y": "Year range"})

    format = request.args.get('format', 'html')
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format', 400

