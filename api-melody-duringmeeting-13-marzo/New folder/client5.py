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

def plotChart(query: str, chart_type: str, endpoint: str, format: str):
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
    
    x_var, y_var = _identify_variables(variable_names, values)

    counts, labels, artwork_labels = _prepare_data(x_var, y_var, values, data)

    # If there's no data, return a message
    if len(counts) == 0 and len(labels) == 0:
        return "No data available."
    # If there's only one count and one label, return count and label as text
    elif len(counts) == 1 and len(labels) == 1:
        return f"Label: {labels[0]}, Count: {counts[0]}"
    # If there's only one count and no labels, return count as text
    elif len(counts) == 1 and len(labels) == 0:
        return f"Count: {counts[0]}"
    # If there's only one count, return count as text
    elif len(counts) == 1:
        return f"Count: {counts[0]}"
    else:
        # Create DataFrame and visualize it.
        df = pd.DataFrame({'labels': labels, 'counts': counts, 'artwork_labels': artwork_labels})
        return _create_visualization(df, x_var, y_var, chart_type, format)


def _identify_variables_1(variable_names: List[str], values: dict) -> tuple:
    if 'height' in variable_names and 'width' in variable_names:
        x_var, y_var = 'height', 'width'
    else:
        count_variables = [var for var in variable_names if 'count' in var.lower()]
        non_count_variables = [var for var in variable_names if var not in count_variables]
        if count_variables:
            y_var = count_variables[0]
            x_var = non_count_variables[0] if non_count_variables else 'label'
        else:
            x_var, y_var = variable_names[0], variable_names[1]
    return x_var, y_var

def _identify_variables_2(variable_names: List[str], values: dict) -> tuple:      # it prints: Label: 9, Count: pythons works with _prepare_data_2
    if 'height' in variable_names and 'width' in variable_names:
        x_var, y_var = 'height', 'width'
    elif 'x' in variable_names and 'count' in variable_names:
        # If 'x' is count and 'count' is label, swap them
        if values['x'][0].isdigit() and not values['count'][0].isdigit():
            x_var, y_var = 'count', 'x'
        else:
            x_var, y_var = 'x', 'count'
    else:
        count_variables = [var for var in variable_names if 'count' in var.lower()]
        non_count_variables = [var for var in variable_names if var not in count_variables]
        if count_variables:
            y_var = count_variables[0]
            x_var = non_count_variables[0] if non_count_variables else 'label'
        else:
            x_var, y_var = variable_names[0], variable_names[1]
    return x_var, y_var

def _identify_variables_3(variable_names: List[str], values: dict) -> tuple:  #again Label: 9, Count: pythons works with _prepare_data_2
    # First, check if 'height' and 'width' variables are present
    if 'height' in variable_names and 'width' in variable_names:
        return 'height', 'width'

    # Second, try to identify count and label variables based on their values
    count_variables = [var for var in variable_names if values[var][0] is not None and values[var][0].isdigit()]
    non_count_variables = [var for var in variable_names if values[var][0] is not None and not values[var][0].isdigit()]

    if count_variables and non_count_variables:
        return non_count_variables[0], count_variables[0]
        
    # If the above two checks didn't work, use a fallback method: 
    # The first variable is assumed to be the label, the second to be the count
    return variable_names[0], variable_names[1]

def _identify_variables_4(variable_names: List[str], values: dict) -> tuple:      # with _prepare_data_3 again label 9 count pythons
    # First, check if 'height' and 'width' variables are present
    if 'height' in variable_names and 'width' in variable_names:
        return 'height', 'width'

    # Second, try to identify count and label variables based on their names
    count_variables = [var for var in variable_names if 'count' in var.lower()]
    non_count_variables = [var for var in variable_names if var not in count_variables]

    if count_variables and non_count_variables:
        return non_count_variables[0], count_variables[0]

    # If the above two checks didn't work, use a fallback method: 
    # The first variable is assumed to be the label, the second to be the count
    return variable_names[0], variable_names[1]

def _identify_variables(variable_names: List[str], values: dict) -> tuple:
    if 'height' in variable_names and 'width' in variable_names:
        x_var, y_var = 'height', 'width'
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


def _prepare_data_1(x_var: str, y_var: str, values: dict, data: list) -> tuple:
    x_values = [float(val) if val else None for val in values.get(x_var, [])]
    y_values = [float(val) if val else None for val in values.get(y_var, [])]
    artwork_labels = [get_artwork_label(artwork_uri, data) for artwork_uri in values.get('artwork', [])]

    return x_values, y_values, artwork_labels

def _prepare_data_2(x_var: str, y_var: str, values: dict, data: list) -> tuple:
    x_values = [val if val else None for val in values.get(x_var, [])]
    y_values = [int(val) if val and val.isdigit() else None for val in values.get(y_var, [])]  # Ensure count values are integers.
    artwork_labels = [get_artwork_label(artwork_uri, data) for artwork_uri in values.get('artwork', [])]

    return x_values, y_values, artwork_labels

def _prepare_data_3(x_var: str, y_var: str, values: dict, data: list) -> tuple:
    x_values = values.get(x_var, [])
    y_values = values.get(y_var, [])

    # Make sure all count values are integers, if they are not integers, keep them as None
    y_values = [int(val) if isinstance(val, str) and val.isdigit() else None for val in y_values]

    artwork_labels = [get_artwork_label(artwork_uri, data) for artwork_uri in values.get('artwork', [])]

    return x_values, y_values, artwork_labels

def _prepare_data(x_var: str, y_var: str, values: dict, data: list) -> tuple:
    counts = [int(val) if val and val.isdigit() else None for val in values.get(y_var, [])]  # Ensure count values are integers.
    labels = [val if val else None for val in values.get(x_var, [])]
    artwork_labels = [get_artwork_label(artwork_uri, data) for artwork_uri in values.get('artwork', [])]

    return counts, labels, artwork_labels


def _create_visualization(df: pd.DataFrame, x_var: str, y_var: str, chart_type: str, format: str):
    if chart_type == 'bar':
        fig = px.bar(df, x='labels', y='counts', labels={x_var: 'Label', y_var: 'Count'}, title="Counts by Label", height=500, width=500)
    elif chart_type == 'pie':
        fig = px.pie(df, values='counts', names='labels', title="Distribution by Label")
    elif chart_type == 'scatter':
        fig = px.scatter(df, x='labels', y='counts', hover_data=['artwork_labels'], labels={x_var: 'Height', y_var: 'Width'}, title="Artwork Height vs Width", height=500, width=500)
        #fig = px.scatter(df, x='labels', y='counts', hover_data=[x_var, y_var], labels={x_var: 'Height', y_var: 'Width'}, title="Artwork Height vs Width", height=500, width=500)
        
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