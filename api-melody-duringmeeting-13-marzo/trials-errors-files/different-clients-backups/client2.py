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
    var_resp = None
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setTimeout(60)  # Set timeout to 60 seconds
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Extract variable names from the query
    variable_names = extract_variable_names(query)
    print(f"Variable names: {variable_names}")  # Debugging

    # Extract data from results
    data = results["results"]["bindings"]
    print(f"Data: {data}")  # Debugging

    # Match variable names from the query with results
    values = {var: [entry[var]["value"] for entry in data if var in entry] for var in variable_names if any(var in entry for entry in data)}
    print(f"Values: {values}")  # Debugging

    # Identify x and y variables
    #x_var, y_var = variable_names[0], variable_names[1]
    x_var, y_var = 'snakeLabel', 'aliasCount'
    #if len(variable_names) >= 2:
    #    x_var, y_var = variable_names[0], variable_names[1]
    #else:
    #    return "Error: Query must return at least two variables"

    # Check if count is present in the variables and set it as y_var
    if "count" in variable_names:
        y_var = "count"
        other_variables = [var for var in variable_names if var != "count"]
        if other_variables:
            x_var = other_variables[0]
        else:
            return "Error: Query must return at least one variable other than 'count'"



    # Create chart based on chart type
    if chart_type == 'bar':
        counts = [int(val) for val in values.get(y_var, [])]
        labels = values.get(x_var, [])
        category_order = {x_var: sorted(labels)}
        fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500, category_orders=category_order)
        print(f"Counts: {counts}, Labels: {labels}")  # Debugging
        


    elif chart_type == 'pie':
        names_var, values_var = x_var, y_var
        fig = px.pie(values=values[values_var], names=values[names_var])
    else:
        var_resp = 'Invalid chart type'

    if format == 'html':
        var_resp = fig.to_html()
    elif format == 'png':
        var_resp = fig.to_image(format='png')
    else:
        var_resp = 'Invalid format'

    return var_resp

'''
SELECT ?x (COUNT(?alias) AS ?count)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q184023 wd:Q184022} # Python, Cobra, and Viper
  ?snake skos:altLabel ?alias . 
  ?snake rdfs:label ?x . # Snake label
  FILTER(LANG(?alias) = "en") # We only count aliases in English
  FILTER(LANG(?x) = "en") # We only want labels in English
}
GROUP BY ?snake ?x

not works
SELECT ?snake ?snakeLabel (COUNT(?alias) AS ?aliasCount)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q184023 wd:Q184022} # Python, Cobra, and Viper
  ?snake rdfs:label ?snakeLabel . # Snake label
  OPTIONAL {?snake skos:altLabel ?alias . FILTER(LANG(?alias) = "en")} # We only count aliases in English if they exist
  FILTER(LANG(?snakeLabel) = "en") # We only want labels in English
}
GROUP BY ?snake ?snakeLabel


works for 2:
SELECT ?snake ?snakeLabel (COUNT(?alias) AS ?aliasCount)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q184023 wd:Q184022} # Python, Cobra, and Viper
  ?snake rdfs:label ?snakeLabel . # Snake label
  OPTIONAL {?snake skos:altLabel ?alias . FILTER(LANG(?alias) = "en")} # We only count aliases in English if they exist
  FILTER(LANG(?snakeLabel) = "en") # We only want labels in English
}
GROUP BY ?snake ?snakeLabel
'''