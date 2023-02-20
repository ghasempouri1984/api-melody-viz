from flask import Flask, request
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

@app.route('/human_count', methods=['GET'])
def human_count():
    min_year = request.args.get('min_year', default=None, type=int)
    max_year = request.args.get('max_year', default=None, type=int)

    query = """
        SELECT (COUNT(?human) AS ?count)
        WHERE {
            ?human wdt:P31 wd:Q5 .
        }
    """

    if min_year is not None:
        query += "FILTER(YEAR(?human) >= {})".format(min_year)
    if max_year is not None:
        query += "FILTER(YEAR(?human) <= {})".format(max_year)

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    data = results["results"]["bindings"]
    count = int(data[0]["count"]["value"])

    fig = px.bar(x=["Humans"], y=[count], labels={"x": "Entity Type", "y": "Count"})
    return fig.to_html()
