################################
# Flask app route:
################################

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



###################################
#The client5.py:
###################################

def extract_variable_names(query):
    select_pattern = r"SELECT\s+(?P<vars>.*?)\s*WHERE"
    select_vars = re.search(select_pattern, query, re.IGNORECASE | re.MULTILINE | re.DOTALL)

    if select_vars:
        select_vars_str = select_vars.group("vars")
        var_pattern = r'\?(?P<var>\w+)'
        variable_names = list(set(re.findall(var_pattern, select_vars_str)))
        print(f"Extracted variable names: {variable_names}")
        return variable_names
    else:
        print("No SELECT clause found in query.")
        return []


def plotChart(query: str, chart_type: str, scatter_x: str, scatter_y: str, endpoint: str, format: str):
    # TODO: You should provide some form of error checking for the inputs here.

    # Initialize the SPARQL client.
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)  # Set timeout to 60 seconds
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()
    print("Received SPARQL query results:")


    # Extract variable names from the query
    variable_names = extract_variable_names(query)

    # Extract data from results
    data = results["results"]["bindings"]

    # Prepare data for plotting.
    values = {var: [entry[var]["value"] if var in entry else None for entry in data] for var in variable_names}
    print(f"Prepared values: {values}")
    
    x_var, y_var = _identify_variables(variable_names, values, scatter_x, scatter_y)

    x_data, y_data = _prepare_data(x_var, y_var, values, chart_type)

    # Create DataFrame and visualize it.
    df = pd.DataFrame({x_var: x_data, y_var: y_data})

    return _create_visualization(df, x_var, y_var, chart_type, format)


def _identify_variables(variable_names: List[str], values: dict, scatter_x: str, scatter_y: str) -> tuple:
    if scatter_x and scatter_y:
        x_var, y_var = scatter_x, scatter_y
    else:
        count_variables = [var for var in variable_names if 'count' in var.lower()]
        non_count_variables = [var for var in variable_names if var not in count_variables]
        if count_variables:
            y_var = count_variables[0]
            x_var = non_count_variables[0] if non_count_variables else 'label'
        else:
            # Ensure x_var is label and y_var is count
            if variable_names[0] == 'x':
                x_var, y_var = variable_names[0], variable_names[1]
            else:
                x_var, y_var = variable_names[1], variable_names[0]
    return x_var, y_var


def _prepare_data(x_var: str, y_var: str, values: dict, chart_type: str) -> tuple:
    x_data = []
    y_data = []

    if x_var in values:
        x_data = _convert_values_to_proper_type(values[x_var])
    if y_var in values:
        y_data = _convert_values_to_proper_type(values[y_var])

    return x_data, y_data


def convert_to_number(val):
    if val is None:
        return None
    try:
        return float(val)
    except ValueError:
        return val

def _convert_values_to_proper_type(values: list) -> list:
    result = []
    for val in values:
        if val is None:
            result.append(None)
        else:
            try:
                result.append(float(val))
            except ValueError:
                result.append(val)
    return result


def _create_visualization(df: pd.DataFrame, x_var: str, y_var: str, chart_type: str, format: str):
    if chart_type == 'bar':
        fig = px.bar(df, x=x_var, y=y_var, labels={x_var: x_var, y_var: y_var}, title="Counts by Label", height=500, width=500)
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_var, names=x_var, title="Distribution by Label")
    elif chart_type == 'scatter':
        hover_data = ['artwork_labels'] if 'artwork_labels' in df.columns else None
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=hover_data, labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
    else:
        return 'Invalid chart type'

    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format'



def get_artwork_label(artwork_uri: str, data: list) -> str:
    # Retrieve artwork label from the results
    for entry in data:
        if entry.get("artwork") and entry["artwork"]["value"] == artwork_uri:
            return entry["artworkLabel"]["value"]
    return None
    
##############################  
# The html template for app:
##############################
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualization App</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <h1>Visualization App</h1>
    <form id="visualization-form">
        <label for="query">SPARQL Query:</label><br>
        <textarea id="query" name="query" rows="4" cols="50" required></textarea><br>
        
        <label for="chart_type">Chart Type:</label><br>
        <select id="chart_type" name="chart_type" required>
            <option value="bar">Bar</option>
            <option value="pie">Pie</option>
            <option value="scatter">Scatter</option>
        </select><br>

        <div id="xy-options" style="display: none;">
            <label for="x_var">X Variable:</label><br>
            <input type="text" id="x_var" name="x_var"><br>
            <label for="y_var">Y Variable:</label><br>
            <input type="text" id="y_var" name="y_var"><br>
        </div>
        
        <label for="format">Format:</label><br>
        <select id="format" name="format" required>
            <option value="html">HTML</option>
            <option value="png">PNG</option>
        </select><br>

        <label for="endpoint">SPARQL Endpoint (Optional):</label><br>
        <input type="text" id="endpoint" name="endpoint" placeholder="https://query.wikidata.org/sparql"><br>

        <input type="submit" value="Submit">
    </form>
    <div id="result"></div>

    <script>
        $("#chart_type").on("change", function() {
            if ($(this).val() === "scatter" || $(this).val() === "bar") {
                $("#xy-options").show();
            } else {
                $("#xy-options").hide();
            }
        });
    
        $("#visualization-form").on("submit", function(event) {
            event.preventDefault();
            const payload = {
                query: $("#query").val(),
                chart_type: $("#chart_type").val(),
                x_var: $("#x_var").val() || undefined,
                y_var: $("#y_var").val() || undefined,
                format: $("#format").val(),
                endpoint: $("#endpoint").val() || undefined
            };
            $.ajax({
                url: "/plot",
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify(payload),
                success: function(response) {
                    if (payload.format === "html") {
                        $("#result").html(response);
                    } else if (payload.format === "png") {
                        const img = new Image();
                        img.src = "data:image/png;base64," + btoa(String.fromCharCode.apply(null, new Uint8Array(response)));
                        $("#result").html(img);
                    }
                },
                error: function(error) {
                    $("#result").text("An error occurred: " + error.responseJSON.error);
                }
            });
            
        });
    </script>
    <script>
        $(document).ready(function() {
            if ($("#chart_type").val() === "scatter" || $("#chart_type").val() === "bar") {
                $("#xy-options").show();
            } else {
                $("#xy-options").hide();
            }
        });
    </script>
    
</body>
</html>
