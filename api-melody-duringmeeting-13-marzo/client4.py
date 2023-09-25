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

def plotChart0(query, chart_type, endpoint, format):
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
    x_var, y_var = 'snakeLabel', 'aliasCount'

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
        if len(labels) > 1:
            category_order = {x_var: sorted(labels)}
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500, category_orders=category_order)
        else:
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)
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

def plotChartworks(query, chart_type, endpoint, format):
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
    #values = {var: [entry[var]["value"] for entry in data if var in entry] for var in variable_names if any(var in entry for entry in data)}
    values = {var: [entry.get(var, {}).get("value", None) for entry in data] for var in variable_names}
    print(f"Values: {values}")  # Debugging

    # If values dictionary is empty, return an appropriate response
    if not values:
        return "Error: No data returned from the SPARQL query"

    # Identify x and y variables
    x_var, y_var = 'snakeLabel', 'aliasCount'

    # Create chart based on chart type
    if chart_type == 'bar':
        counts = [int(val) for val in values.get(y_var, [])]
        labels = values.get(x_var, [])
        
        # Prepare text for each bar in the chart
        hover_text = []
        for i in range(len(labels)):
            hover_text.append('<br>'.join(f"{var}: {values[var][i]}" for var in variable_names if var not in {x_var, y_var}))
        
        if len(labels) > 1:
            category_order = {x_var: sorted(labels)}
            fig = px.bar(x=labels, y=counts, text=hover_text, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500, category_orders=category_order)
        else:
            fig = px.bar(x=labels, y=counts, text=hover_text, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)

        fig.update_traces(hovertemplate='%{text}<br>'+y_var+': %{y}<extra></extra>')  # Customize hover label

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

def plotChartforboth(query, chart_type, endpoint, format):
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
    if len(variable_names) > 1:
        # Original logic when multiple variables are present
        x_var, y_var = 'snakeLabel', 'aliasCount'
        if "count" in variable_names:
            y_var = "count"
            other_variables = [var for var in variable_names if var != "count"]
            if other_variables:
                x_var = other_variables[0]
    else:
        # Special case for only one variable in response
        x_var = 'label'
        y_var = 'count'
        if y_var in values:
            values[x_var] = ['Humans']

    # Create chart based on chart type
    if chart_type == 'bar':
        counts = [int(val) for val in values.get(y_var, [])]
        labels = values.get(x_var, [])
        if len(labels) > 1:
            category_order = {x_var: sorted(labels)}
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500, category_orders=category_order)
        else:
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)
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

def plotChartonlyshowshuman(query, chart_type, endpoint, format):
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
    x_var = 'label'
    y_var = 'count'
    
    # Create default label if necessary
    if y_var in values and len(values) == 1:
        values[x_var] = ['Humans']

    # Create chart based on chart type
    if chart_type == 'bar':
        counts = [int(val) for val in values.get(y_var, [])]
        labels = values.get(x_var, [])
        if len(labels) > 1:
            category_order = {x_var: sorted(labels)}
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500, category_orders=category_order)
        else:
            fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)
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
    count_variables = [var for var in variable_names if 'count' in var.lower()]
    non_count_variables = [var for var in variable_names if var not in count_variables]
    if count_variables:
        y_var = count_variables[0]
        if non_count_variables:
            # Choose the most appropriate non-count variable
            x_var = non_count_variables[-1]  
        else:
            x_var = 'label'
            values[x_var] = ['Result']  # add default label
    else:
        x_var, y_var = variable_names[0], variable_names[1]

    # Create chart based on chart type
    counts = [int(val) for val in values.get(y_var, [])]
    labels = values.get(x_var, [])
    print(f"Counts: {counts}, Labels: {labels}")  # Debugging

    if chart_type == 'bar':
        fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)
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


def plotChart_(query, chart_type, endpoint, format):
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
    count_variables = [var for var in variable_names if 'count' in var.lower()]
    non_count_variables = [var for var in variable_names if var not in count_variables]
    if count_variables:
        y_var = count_variables[0]
        if non_count_variables:
            # Choose the most appropriate non-count variable
            x_var = non_count_variables[0]  
        else:
            x_var = 'label'
            values[x_var] = ['Result']  # add default label
    else:
        x_var, y_var = variable_names[0], variable_names[1]

    # Create chart based on chart type
    print(f"x_var: {x_var}, y_var: {y_var}")  # Debugging
    counts = [int(val) for val in values.get(y_var, [])]
    labels = values.get(x_var, [])
    print(f"Counts: {counts}, Labels: {labels}")  # Debugging

    # If there's no data, return a message
    if len(counts) == 0 and len(labels) == 0:
        return "No data available."

    # If there's only one count and no labels, return count as text
    if len(counts) == 1 and len(labels) == 0:
        return f"Count: {counts[0]}"

    if chart_type == 'bar':
        fig = px.bar(x=labels, y=counts, labels={x_var: '', y_var: ''}, title="Number of items", height=500, width=500)
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
'''