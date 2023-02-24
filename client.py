import requests
import json

def plotChart(query, chart_type, endpoint, format):
    var_resp=None
    #url = 'http://localhost:5000/plot'
    # Set up SPARQL query
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)  # Set timeout to 60 seconds
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract data from results
    data = results["results"]["bindings"]

    # Create chart based on chart type
    if chart_type == 'bar':
        count = data[0]["count"]["value"]
    
        # Get custom labels from query result, default to 'Count' if not specified
        label_x = data[0]["label_x"]["value"] if "label_x" in data[0] else 'Count'
        label_y = data[0]["label_y"]["value"] if "label_y" in data[0] else 'Count'
        fig = px.bar(x=[label_x], y=[count], labels={'x':'', 'y':label_y})

    elif chart_type == 'pie':
        fig = px.pie(values=[count], names=[label_x])
    else:
    #    return 'Invalid chart type', 400
        var_resp= 'Invalid chart type'

    # Get format from JSON payload, default to HTML if not specified
    #format = req_data.get('format', 'html')

    # Return chart in the requested format
    if format == 'html':
        #return fig.to_html()
        var_resp=fig.to_html()
    elif format == 'png':
        var_resp = fig.to_image(format='png')
        #return Response(png_image, mimetype='image/png')

    else:
        var_resp='Invalid format'

    #response = requests.post(url, json=params)
    #print(response.text)
    if params['format'] == 'html':
        with open('output2.html', 'wb') as file:
            #file.write(response.text)
            #file.write(response.text.encode('utf-8', 'ignore').decode('utf-8'))
            #file.write(response.text.encode('utf-8'))
            file.write(var_resp.text.encode('utf-8'))
            
    elif params['format'] == 'png':
        with open('chart.png', 'wb') as file:
            #file.write(response.content)
            file.write(var_resp.content)
    return var_resp
    
