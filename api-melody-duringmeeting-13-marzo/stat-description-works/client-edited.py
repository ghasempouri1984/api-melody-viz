
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
                result.append(val)
    return result


def _create_visualization(df: pd.DataFrame, x_var: str, y_var: str, scatter_label: str, chart_type: str, format: str):
    
    # Debugging: Inspect the first few rows of the DataFrame
    print(f"Creating DataFrame with x_var: {x_var}, y_var: {y_var}")
    print("DataFrame head:")
    print(df.head())
    # Debugging: Check the data types of each column
    print("Data types in DataFrame:")
    print(df.dtypes)

    # Debugging: Validate Variable Names
    print(f"Variable names: x_var = {x_var}, y_var = {y_var}")
    
    # Debugging: Check for NaN or None values in x_var and y_var
    print("NaN or None counts:")
    print(df[x_var].isna().sum(), df[y_var].isna().sum())

    if chart_type == 'scatter' and not all(isinstance(x, (int, float)) for x in df[x_var]):
        return f"The X variable must contain numerical values for plotting a {chart_type} chart.", None

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
        '''
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=[scatter_label], labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
        # Calculate statistics here if needed

        # Calculate statistics
        x_values = df[x_var]
        y_values = df[y_var]
        stats = {
            'x_min': x_values.min(),
            'x_max': x_values.max(),
            'x_mean': x_values.mean(),
            'x_median': x_values.median(),
            'y_min': y_values.min(),
            'y_max': y_values.max(),
            'y_mean': y_values.mean(),
            'y_median': y_values.median(),
        }

        # Generate summary
        summary = f"The minimum and maximum values for the x variable are {stats['x_min']} and {stats['x_max']}, respectively. The mean and median values are {stats['x_mean']} and {stats['x_median']}, respectively. "
        summary += f"The minimum and maximum values for the y variable are {stats['y_min']} and {stats['y_max']}, respectively. The mean and median values are {stats['y_mean']} and {stats['y_median']}, respectively. "

        stats['summary'] = summary
        '''

        # Generate plot
        fig = px.scatter(df, x=x_var, y=y_var, hover_data=[scatter_label], labels={x_var: x_var, y_var: y_var}, title=f"{x_var} vs {y_var}", height=500, width=500)
        

        # Fill with zeros
        df[x_var] = df[x_var].fillna(0)
        df[y_var] = df[y_var].fillna(0)
        # Calculate statistics
        x_values = df[x_var]
        y_values = df[y_var]

        try:
        # Calculate correlation
            correlation = x_values.corr(y_values)

            # Calculate linear regression
            slope, intercept, r_value, p_value, std_err = linregress(x_values, y_values)
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