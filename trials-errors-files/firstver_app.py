import json
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/plot', methods=['POST'])
def plot():
    # Get query and chart type from JSON payload
    req_data = request.get_json()
    query = req_data.get('query')
    chart_type = req_data.get('chart_type', 'bar')

    # Get SPARQL endpoint from JSON payload, default to Wikidata if not specified
    endpoint = req_data.get('endpoint', 'https://query.wikidata.org/sparql')

    # Set up SPARQL query
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)  # Set timeout to 60 seconds
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract data from results
    data = results["results"]["bindings"]
    count = data[0]["count"]["value"]

    # Create chart based on chart type
    if chart_type == 'bar':
        fig = px.bar(x=['Humans'], y=[count], labels={'x':'', 'y':'Count of Humans'})
    elif chart_type == 'pie':
        fig = px.pie(values=[count], names=['Humans'])
    else:
        return 'Invalid chart type', 400

    # Get format from JSON payload, default to HTML if not specified
    format = req_data.get('format', 'html')

    # Return chart in the requested format
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        png_image = fig.to_image(format='png')
        return Response(png_image, mimetype='image/png')
    else:
        return 'Invalid format', 400
