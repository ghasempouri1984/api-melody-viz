import requests
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import plotly.express as px
import re  # Add this import to use regular expressions
import pandas as pd
from typing import List
from scipy.stats import linregress
from pandas.api.types import is_numeric_dtype



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
    
    # Add debug line here to check the variables being used to create the DataFrame
    print(f"Creating DataFrame with x_var: {x_var}, y_var: {y_var}")
    
    if chart_type == 'bar':
        x_data, y_data = _prepare_bar_pie_data(x_var, y_var, values)  # Make sure x_var, y_var match SPARQL results
        df = pd.DataFrame({x_var: x_data, y_var: y_data})

    # Create DataFrame and visualize it.
    if chart_type == 'scatter':
        x_data, y_data, labels = _prepare_scatter_data(x_var, y_var, scatter_label, values)
        df = pd.DataFrame({x_var: x_data, y_var: y_data, scatter_label: labels})
    else:
        x_data, y_data = _prepare_bar_pie_data(x_var, y_var, values)
        df = pd.DataFrame({x_var: x_data, y_var: y_data})
    
    # Add this line to check the DataFrame before plotting
    print("DataFrame before plotting:")
    print(df)
    
    # Remove the column labeled 'None' if it exists
    if None in df.columns:
        del df[None]
    
    # Convert numerical columns to the appropriate data type
    df[y_var] = pd.to_numeric(df[y_var], errors='coerce')

    # Add debugging statements here
    print("Data types in DataFrame before plotting:")
    print(df.dtypes)
    print("Checking for None or NaN values in DataFrame:")
    print(df.isna().sum())

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

    if x_var in values and y_var in values:
        min_length = min(len(values[x_var]), len(values[y_var]))
        x_data = _convert_values_to_proper_type(values[x_var][:min_length])
        y_data = _convert_values_to_proper_type(values[y_var][:min_length])

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
                try:
                    result.append(int(val))
                except ValueError:
                    result.append(val)
    return result

def _create_visualization(df: pd.DataFrame, x_var: str, y_var: str, scatter_label: str, chart_type: str, format: str):
    
    # Check for an empty DataFrame
    #if df.empty:
    #    return "The DataFrame is empty. Cannot generate plot.", None
    
    # Debugging: Inspect the first few rows of the DataFrame
    print(f"Creating DataFrame with x_var: {x_var}, y_var: {y_var}")
    print("DataFrame head:")
    print(df.head())
    # Debugging: Check the data types of each column
    print("Data types in DataFrame:")
    print(df.dtypes)
    
    # Numeric conversion for scatter plot
    #if chart_type == 'scatter':
     #   try:
      #      df[x_var] = pd.to_numeric(df[x_var])
       # except Exception as e:
        #    return f"Error in converting x_var to numeric for {chart_type} chart: {e}", None

    # Check if the specified columns exist in DataFrame
    if x_var not in df.columns or y_var not in df.columns:
        return f"Columns {x_var} or {y_var} not found in DataFrame.", None
    
     # Verify if Y variable is appropriate for calculations
    if not (df[y_var].dtype in ['int64', 'float64']):
        return "The Y variable must contain numerical values for plotting.", None
    
    # Debugging: Validate Variable Names
    print(f"Variable names: x_var = {x_var}, y_var = {y_var}")
    
    # Debugging: Check for NaN or None values in x_var and y_var
    print("NaN or None counts:")
    print(df[x_var].isna().sum(), df[y_var].isna().sum())
    
    # Debugging: Try converting x_var to numeric if it isn't already
    #try:
    #    df[x_var] = pd.to_numeric(df[x_var])
    #except Exception as e:
    #    print(f"Error in converting x_var: {e}")
    
    # Conditional conversion based on chart type
    if chart_type in ['scatter', 'pie']:  # These types generally require numeric x_var
        try:
            df[x_var] = pd.to_numeric(df[x_var])
        except Exception as e:
            return f"Error in converting x_var to numeric for {chart_type} chart: {e}", None
    
    # Check if x_var and y_var are appropriate for calculations
    if not all(isinstance(x, (int, float)) for x in df[y_var]):
        return f"The Y variable must contain numerical values for plotting a {chart_type} chart.", None

    if chart_type == 'scatter' and not all(isinstance(x, (int, float)) for x in df[x_var]):
        return f"The X variable must contain numerical values for plotting a {chart_type} chart.", None
    
    # Explicit conversion
    df[y_var] = pd.to_numeric(df[y_var], errors='coerce')
    df[x_var] = pd.to_numeric(df[x_var], errors='coerce')

    if chart_type == 'bar':
        fig = px.bar(df, x=x_var, y=y_var, labels={x_var: x_var, y_var: y_var}, title="Counts by Label", height=500, width=500)

        # Calculate statistics
        counts = df[y_var]
        categories = df[x_var]
        stats = {
            'max_count': counts.max(),
            'min_count': counts.min(),
            'total_count': counts.sum(),
            'max_category': categories.loc[counts.idxmax()],
            'min_category': categories.loc[counts.idxmin()],
            'total_categories': len(categories)
        }

        # Generate summary
        summary = f"The category with the highest frequency is '{stats['max_category']}' with a count of {stats['max_count']}. "
        summary += f"The category with the lowest frequency is '{stats['min_category']}' with a count of {stats['min_count']}. "
        summary += f"The total count across all {stats['total_categories']} categories is {stats['total_count']}."

        stats['summary'] = summary
        
    elif chart_type == 'pie':
        fig = px.pie(df, values=y_var, names=x_var, title="Distribution by Label")
        # Calculate statistics here if needed
    elif chart_type == 'scatter':

        if not (df[x_var].dtype in ['int64', 'float64'] and df[y_var].dtype in ['int64', 'float64']):
          return "For scatter plots, both X and Y variables must be numeric.", None

        # Your existing scatter plot code remains mostly unchanged
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=[scatter_label], labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
        
        # Fill with zeros for NaN
        df[x_var] = df[x_var].fillna(0)
        df[y_var] = df[y_var].fillna(0)
        
        try:
            # Calculate correlation and linear regression
            correlation = df[x_var].corr(df[y_var])
            slope, intercept, r_value, p_value, std_err = linregress(df[x_var], df[y_var])
        except Exception as e:
            print("Error calculating statistics: ", str(e))
            correlation, slope, intercept, r_value, p_value, std_err = [None]*6

        stats = {
            'correlation': correlation,
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value': p_value,
            'std_err': std_err
        }
        
        # Generate summary
        summary = f"The correlation between the variables is {round(stats['correlation'], 2)}. "
        summary += f"The equation of the regression line is y = {round(stats['slope'], 2)}*x + {round(stats['intercept'], 2)}. "
        summary += f"The r-squared value is {round(stats['r_value']**2, 2)}, the p-value is {round(stats['p_value'], 2)}, and the standard error is {round(stats['std_err'], 2)}."
        stats['summary'] = summary


    else:
        return 'Invalid chart type', None

    if format == 'html':
        return fig.to_html(), stats
    elif format == 'png':
        return fig.to_image(format='png'), stats
    else:
        return 'Invalid format', None



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

4 snakeLabels:

SELECT ?snake ?snakeLabel (COUNT(?alias) AS ?aliasCount)
WHERE
{
  VALUES ?snake {wd:Q184018 wd:Q194425 wd:Q12061410 wd:Q3887135} # pythons, and Mamba
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