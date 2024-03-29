import json
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request, Response , render_template
from flask import jsonify
import client

app = Flask(__name__)

@app.route('/plot', methods=['POST', 'GET'])

@app.route('/plot', methods=['POST', 'GET'])
def plot():
    if request.method == 'GET':
        return render_template('index.html')
                             
    if request.method == 'POST':
        try:
            # Get data from JSON payload
            req_data = request.get_json()
            query = req_data.get('query')
            chart_type = req_data.get('chart_type', 'bar')
            format = req_data.get('format', 'html')

            # Validate format
            if format not in ['html', 'png']:
                return jsonify({"error": "Invalid format"}), 400

            # Debug lines
            print("About to call the plotting function.")

            # Additional code for plotting
            endpoint = req_data.get('endpoint', 'https://query.wikidata.org/sparql')
            x_var = req_data.get('x_var')
            y_var = req_data.get('y_var')
            scatter_label = req_data.get('scatter_label')

            # Call the plotting function
            fig, stats = client.plotChart(query, chart_type, x_var, y_var, scatter_label, endpoint, format)

            # Debug lines
            print("Plotting function was called.")
            print("Preparing to send response...")

            # Prepare and send the response
            response = {'fig': fig, 'stats': stats}
            #print("Sending response:", response)
            return jsonify(response)
            
        except Exception as e:
            print("An exception occurred:", e)  # Debug line for exceptions
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run()