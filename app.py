import json
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, Response
import client

app = Flask(__name__)

@app.route('/plot', methods=['POST'])
def plot():
    # Get query and chart type from JSON payload
    req_data = request.get_json()
    query = req_data.get('query')
    chart_type = req_data.get('chart_type', 'bar')
    format = req_data.get('format', 'html')

    # Get SPARQL endpoint from JSON payload, default to Wikidata if not specified
    endpoint = req_data.get('endpoint', 'https://query.wikidata.org/sparql')
    resp=client.plotChart(query, chart_type, endpoint, format)
    #according to format we return different response
    return resp