import json
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, Response , render_template
from flask import jsonify
import client
import numpy as np

app = Flask(__name__)

def json_serial(obj):
    print("Attempting to serialize: ", type(obj))
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError("Type not serializable")

@app.route('/plot', methods=['POST', 'GET'])

def plot():
    if request.method == 'GET':
        return render_template('index3.html') 
                             
    if request.method == 'POST':
        try:
            # Get query and chart type from JSON payload
            req_data = request.get_json()
            query = req_data.get('query')
            chart_type = req_data.get('chart_type', 'bar')
            format = req_data.get('format', 'html')

            # Get SPARQL endpoint from JSON payload, default to Wikidata if not specified
            #endpoint = req_data.get('endpoint', 'https://query.wikidata.org/sparql')
            endpoint = req_data.get('endpoint', 'http://localhost:9999/blazegraph/namespace/myTest/sparql')

            # Get scatter plot variables from JSON payload
            x_var = req_data.get('x_var')
            y_var = req_data.get('y_var')
            scatter_label = req_data.get('scatter_label')

            #resp = client.plotChart(query, chart_type, x_var, y_var, scatter_label, endpoint, format)
            fig, stats = client.plotChart(query, chart_type, x_var, y_var, scatter_label, endpoint, format)
            #print("Stats before serialization: ", stats)

            # Convert stats dictionary to JSON format using custom serialization
            #json_stats = json.dumps(stats, default=json_serial)
            #print("Serialized JSON Stats: ", json_stats)
            #according to format we return different response
            if format == 'html':
                return jsonify({'fig': fig, 'stats': stats})
            elif format == 'png':
                return jsonify({'fig': fig, 'stats': stats})
            else:
                return jsonify({"error": "Invalid format"}), 400
         
            #according to format we return different response
            #return resp
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()