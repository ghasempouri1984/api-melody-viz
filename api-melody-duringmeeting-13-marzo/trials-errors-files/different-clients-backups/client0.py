import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import plotly.express as px

import re

def extract_variable_names(query):
    variable_pattern = re.compile(r'\?(\w+)')
    variable_names = variable_pattern.findall(query)
    return variable_names


def plotChart(query, chart_type, endpoint, format):
    var_resp=None

    variable_names = extract_variable_names(query)
    if len(variable_names) < 2:
        return 'two variables (label and count) must be present in the query.'

    label_x = variable_names[0]
    label_y = variable_names[1]


    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)  # Set timeout to 60 seconds
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract data from results
    data = results["results"]["bindings"]
    #count = data[0]["count"]["value"]
    count = data[0][label_y]["value"]

    # Get custom labels from query result, default to 'Count' if not specified
    label_x = data[0]["label_x"]["value"] if "label_x" in data[0] else 'Count'
    label_y = data[0]["label_y"]["value"] if "label_y" in data[0] else 'Count'
    # Create chart based on chart type
    if chart_type == 'bar':
        
        #fig = px.bar(x=[label_x], y=[count], labels={'x':'', 'y':label_y})
        #fig = px.bar(x=[label_x], y=[count], labels={'x':'', 'y':label_y}, title="Number of items", height=500, width=500)
        fig = px.bar(x=[label_x], y=[label_y], labels={'x':'', 'y':label_y}, title="Number of items", height=500, width=500)


    elif chart_type == 'pie':
        #fig = px.pie(values=[count], names=[label_x])
        counts = [entry["label_y"]["value"] for entry in data]
        labels = [entry["label_x"]["value"] for entry in data]
        fig = px.pie(values=counts, names=labels)
    else:
        var_resp= 'Invalid chart type'

    if format == 'html':
        var_resp=fig.to_html()
    elif format == 'png':
        var_resp = fig.to_image(format='png')
        
    else:
        var_resp='Invalid format'


    return var_resp
    
