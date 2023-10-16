# Initializing the Flask application
app = Flask(__name__)

# Defining the /plot route to handle both GET and POST requests
@app.route('/plot', methods=['GET', 'POST'])
def plot_route():
    if request.method == 'GET':
        # Rendering the index.html template to display the user interface
        return render_template('index.html')
    
    elif request.method == 'POST':
        # Extracting JSON payload from the incoming request
        payload = json.loads(request.data)

        # Performing SPARQL queries and generating charts using the custom client module
        # For example: chart_data, stats = custom_client_module.create_chart(payload)
        
        # Returning the chart and stats as a JSON response
        return jsonify({
            'chart': 'Serialized_Chart_Data_Here', 
            'stats': 'Serialized_Stats_Here'
        })

# Running the Flask application
if __name__ == '__main__':
    app.run(debug=True)