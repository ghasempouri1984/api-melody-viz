from flask import Flask, request
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

@app.route('/chart', methods=['GET'])
def chart():
    query_template = """
        SELECT (COUNT(?human) AS ?count)
        WHERE {
            ?human wdt:P31 wd:Q5 .
        }
    """
    chart_type = request.args.get('chart_type', 'bar')
    chart_types = {'bar': px.bar, 'line': px.line, 'scatter': px.scatter}
    if chart_type not in chart_types:
        return 'Invalid chart type', 400
    chart_fn = chart_types[chart_type]

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query_template)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Decide how to create a chart based on the results
    data = results["results"]["bindings"]
    fig = chart_fn(data_frame={'Count': [int(item["count"]["value"]) for item in data]})

    format = request.args.get('format', 'html') # Get the format from the URL query string, defaulting to 'html'
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format', 400
