import json
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, Response , render_template
from flask import jsonify
import client5

app = Flask(__name__)

@app.route('/plot', methods=['POST', 'GET'])
def plot():
    if request.method == 'GET':
        return render_template('index.html') 
                             
    if request.method == 'POST':
        try:
            # Get query and chart type from JSON payload
            req_data = request.get_json()
            query = req_data.get('query')
            chart_type = req_data.get('chart_type', 'bar')
            format = req_data.get('format', 'html')

            # Get SPARQL endpoint from JSON payload, default to Wikidata if not specified
            endpoint = req_data.get('endpoint', 'https://query.wikidata.org/sparql')

            # Get scatter plot variables from JSON payload
           # scatter_x = req_data.get('scatter_x')
            #scatter_y = req_data.get('scatter_y')
            x_var = req_data.get('x_var')
            y_var = req_data.get('y_var')


            #resp = client5.plotChart(query, chart_type, endpoint, format, scatter_x, scatter_y)
            #resp = client5.plotChart(query, chart_type, scatter_x, scatter_y, endpoint, format)
            resp = client5.plotChart(query, chart_type, x_var, y_var, endpoint, format)


         
            #according to format we return different response
            return resp
        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()