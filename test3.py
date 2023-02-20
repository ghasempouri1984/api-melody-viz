from flask import Flask, request
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)

@app.route('/chart', methods=['GET'])
def chart():
    artist_id = "Q1089074" # Replace with the Wikidata ID of the desired artist

    query_template = """
        SELECT ?title ?year
        WHERE {{
          ?artwork wdt:P170 wd:{artist_id} ;
                   wdt:P31 wd:Q3305213 ;
                   wdt:P571 ?date ;
                   wdt:P1476 ?title .
          FILTER (YEAR(?date) >= {min_year} && YEAR(?date) <= {max_year})
          BIND(YEAR(?date) AS ?year)
        }}
    """
    min_year = request.args.get('min_year', default=1900, type=int) # Get the minimum year from the URL query string, defaulting to 1900
    max_year = request.args.get('max_year', default=2000, type=int) # Get the maximum year from the URL query string, defaulting to 2000
    query = query_template.format(artist_id=artist_id, min_year=min_year, max_year=max_year)

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    data = results["results"]["bindings"]
    x_col = "year"
    y_col = "title"
    fig = px.bar(x=[item[x_col]["value"] for item in data], y=[item[y_col]["value"] for item in data])

    format = request.args.get('format', 'html')
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format', 400
