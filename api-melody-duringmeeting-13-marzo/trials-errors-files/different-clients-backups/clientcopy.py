import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import plotly.express as px
import re  # Add this import to use regular expressions


def extract_variable_names(query):
    select_pattern = r"SELECT\s+(?P<vars>.*?)\s*WHERE"
    select_vars = re.search(select_pattern, query, re.IGNORECASE | re.MULTILINE | re.DOTALL)

    if select_vars:
        select_vars_str = select_vars.group("vars")
        var_pattern = r'\?(?P<var>\w+)'
        return list(set(re.findall(var_pattern, select_vars_str)))
    else:
        return []

def plotChart(query, chart_type, endpoint, format):
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract the variable names from the SELECT clause of the query
    variable_names = [var.strip('?') for var in query.split('SELECT')[1].split('WHERE')[0].strip().split()]

    # Extract the data from the SPARQL query results
    data = results["results"]["bindings"]

    # Extract the values for each variable from the data
    values = {var: [entry[var]["value"] for entry in data] for var in variable_names if var in data[0]}

    # Identify the x and y variables based on their order in the variable_names list
    x_var, y_var = variable_names[:2]

    # Create the chart based on the chart type
    if chart_type == 'bar':
        fig = px.bar(x=values[x_var], y=values[y_var], labels={x_var: '', y_var: ''})
    elif chart_type == 'pie':
        fig = px.pie(values=values[y_var], names=values[x_var])
    else:
        return 'Invalid chart type'

    # Render the chart in the requested format
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format'


