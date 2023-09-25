import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import plotly.express as px
import re  # Add this import to use regular expressions
import pandas as pd
from typing import List



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


def plotChart_(query: str, chart_type: str, scatter_x: str, scatter_y: str, scatter_label: str, endpoint: str, format: str):
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
    
    #x_var, y_var = _identify_variables(variable_names, values, scatter_x, scatter_y, scatter_label)
    x_var, y_var = _identify_variables(variable_names, values, scatter_x, scatter_y)
    
    x_data, y_data, labels = _prepare_data(x_var, y_var, scatter_label, values, chart_type)

    # Create DataFrame and visualize it.
    if chart_type == 'scatter':
        #df = pd.DataFrame({x_var: x_data, y_var: y_data, 'label': labels})
        df = pd.DataFrame({x_var: x_data, y_var: y_data, scatter_label: labels})
    else:
        df = pd.DataFrame({x_var: x_data, y_var: y_data})

    print(f"Scatter Label: {scatter_label}")
    print(f"Variable Names: {variable_names}")
    print(df)


    #return _create_visualization(df, x_var, y_var, 'label', chart_type, format)
    return _create_visualization(df, x_var, y_var, scatter_label, chart_type, format)

def plotChart(query: str, chart_type: str, scatter_x: str, scatter_y: str, scatter_label: str, endpoint: str, format: str):
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

    # Create DataFrame and visualize it.
    if chart_type == 'scatter':
        x_data, y_data, labels = _prepare_scatter_data(x_var, y_var, scatter_label, values)
        df = pd.DataFrame({x_var: x_data, y_var: y_data, scatter_label: labels})
    else:
        x_data, y_data = _prepare_bar_pie_data(x_var, y_var, values)
        df = pd.DataFrame({x_var: x_data, y_var: y_data})

    return _create_visualization(df, x_var, y_var, scatter_label, chart_type, format)




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


def _prepare_data_(x_var: str, y_var: str, label_var: str, values: dict, chart_type: str) -> tuple:

    x_data = []
    y_data = []

    if x_var in values:
        x_data = _convert_values_to_proper_type(values[x_var])
    if y_var in values:
        y_data = _convert_values_to_proper_type(values[y_var])
    if label_var in values:
        labels = values[label_var]
    else:
        labels = [None] * len(x_data) # If 'label_var' doesn't exist, create a list of None values

    return x_data, y_data, label_var

def _prepare_data_(x_var: str, y_var: str, label_var: str, values: dict, chart_type: str) -> tuple:

    x_data = []
    y_data = []

    if x_var in values:
        x_data = _convert_values_to_proper_type(values[x_var])
    if y_var in values:
        y_data = _convert_values_to_proper_type(values[y_var])
    if label_var in values:
        labels = values[label_var]
    else:
        labels = [None] * len(x_data) # If 'label_var' doesn't exist, create a list of None values

    return x_data, y_data, labels

def _prepare_scatter_data(x_var: str, y_var: str, label_var: str, values: dict) -> tuple:

    x_data = []
    y_data = []

    if x_var in values:
        x_data = _convert_values_to_proper_type(values[x_var])
    if y_var in values:
        y_data = _convert_values_to_proper_type(values[y_var])
    if label_var in values:
        labels = values[label_var]
    else:
        labels = [None] * len(x_data) # If 'label_var' doesn't exist, create a list of None values

    return x_data, y_data, labels


def _prepare_bar_pie_data(x_var: str, y_var: str, values: dict) -> tuple:

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


def _create_visualization_(df: pd.DataFrame, x_var: str, y_var: str, label_var: str, chart_type: str, format: str):

    if chart_type == 'bar':
        fig = px.bar(df, x=x_var, y=y_var, label_var={x_var: x_var, y_var: y_var}, title="Counts by Label", height=500, width=500)
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_var, names=x_var, title="Distribution by Label")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=[label_var], labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
        
    else:
        return 'Invalid chart type'

    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format'
    
def _create_visualization__(df: pd.DataFrame, x_var: str, y_var: str, label_var: str, chart_type: str, format: str):

    hover_data = {label_var: True} if label_var in df.columns else None

    if chart_type == 'bar':
        fig = px.bar(df, x=x_var, y=y_var, hover_data=hover_data, labels={x_var: x_var, y_var: y_var}, title="Counts by Label", height=500, width=500)
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_var, names=x_var, title="Distribution by Label")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=hover_data, labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
    else:
        return 'Invalid chart type'

    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format'
    
def _create_visualization(df: pd.DataFrame, x_var: str, y_var: str, scatter_label: str, chart_type: str, format: str):

    if chart_type == 'bar':
        fig = px.bar(df, x=x_var, y=y_var, labels={x_var: x_var, y_var: y_var}, title="Counts by Label", height=500, width=500)
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_var, names=x_var, title="Distribution by Label")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=[scatter_label], labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
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

'''
for this just print counts like ?human query:
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


works for 2 and plots bars:
SELECT ?snake ?snakeLabel (COUNT(?alias) AS ?aliasCount)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q184023 wd:Q184022} # Python, Cobra, and Viper
  ?snake rdfs:label ?snakeLabel . # Snake label
  OPTIONAL {?snake skos:altLabel ?alias . FILTER(LANG(?alias) = "en")} # We only count aliases in English if they exist
  FILTER(LANG(?snakeLabel) = "en") # We only want labels in English
}
GROUP BY ?snake ?snakeLabel


works with new plotChart and plots:
SELECT ?snake ?snakeLabel (COUNT(?alias) AS ?aliasCount)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q194425} # pythons, and Mamba
  ?snake rdfs:label ?snakeLabel . # Snake label
  OPTIONAL {?snake skos:altLabel ?alias . FILTER(LANG(?alias) = "en")} # We only count aliases in English if they exist
  FILTER(LANG(?snakeLabel) = "en") # We only want labels in English
}
GROUP BY ?snake ?snakeLabel

now also works and just prints counts no bars:
SELECT (COUNT(?human) AS ?count)
        WHERE {
            ?human wdt:P31 wd:Q5 .
        }

returns no data available:
SELECT ?continentLabel (COUNT(DISTINCT ?snake) AS ?count)
WHERE {
  ?snake wdt:P31 wd:Q10884;  # P31 is the property for "instance of", and Q10884 for "species"
         wdt:P171* wd:Q25376.  # P171 is the property for "parent taxon", and Q25376 for "snake"
  ?snake wdt:P183 ?country.  # P183 is the property for "endemism"
  ?country wdt:P30 ?continent.  # P30 is the property for "continent"
  ?continent rdfs:label ?continentLabel. 
  FILTER(LANG(?continentLabel) = "en")  # English labels
}
GROUP BY ?continentLabel
ORDER BY DESC(?count)


challenge is scatter:
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX wd: <http://www.wikidata.org/entity/> 
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX v: <http://www.wikidata.org/prop/statement/>

SELECT ?artwork ?artworkLabel (SAMPLE(?kms) AS ?kms) (SAMPLE(?height) AS ?height) (SAMPLE(?width) AS ?width) (SAMPLE(?url) AS ?url) WHERE {	
   ?artwork wdt:P195 wd:Q671384 .  # SMK
   ?artwork wdt:P170 wd:Q979541 .  # Martinus Rørby
   SERVICE wikibase:label {
     bd:serviceParam wikibase:language "da" .
   } 
   OPTIONAL {?artwork wdt:P217 ?kms } 
   OPTIONAL {?artwork wdt:P2048 ?height } 
   OPTIONAL {?artwork wdt:P2049 ?width } 
   OPTIONAL {?artwork wdt:P973 ?url } 
 }
GROUP BY ?artwork ?artworkLabel
LIMIT 20


'''