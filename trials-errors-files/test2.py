from flask import Flask, request
import plotly.express as px
from SPARQLWrapper import SPARQLWrapper, JSON

app = Flask(__name__)
artist_uri="http://dbpedia.org/resource/Federico_Zeri&min_birth_year=1900&max_birth_year=2000&format=html"

@app.route('/chart', methods=['GET'])
def chart():
    query_template = """
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbpprop: <http://dbpedia.org/property/>

    SELECT ?title ?year ?imageUrl
    WHERE {{
      SELECT ?artwork ?title ?year ?imageUrl
      WHERE {{
        ?artist foaf:name "Federico Zeri" ;
                dbpedia-owl:birthDate ?birthDate .
        FILTER (YEAR(?birthDate) >= 1900 && YEAR(?birthDate) <= 2000)
        ?artwork dbpprop:artist ?artist ;
                 dct:title ?title ;
                 dct:created ?year ;
                 foaf:depiction ?imageUrl .
      }}
      ORDER BY ?year
      LIMIT 10
    }}
    """

    parameter = request.args.get('parameter') # Get the value of the parameter from the URL query string
    query = query_template.format(parameter=parameter) # Insert the parameter value into the SPARQL query

    sparql = SPARQLWrapper("http://example.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Decide how to create a chart based on the results
    data = results["results"]["bindings"]
    x_col = "x" # Replace with the name of the column you want to use for the x-axis
    y_col = "y" # Replace with the name of the column you want to use for the y-axis
    fig = px.line(x=[item[x_col]["value"] for item in data], y=[item[y_col]["value"] for item in data])

    format = request.args.get('format', 'html') # Get the format from the URL query string, defaulting to 'html'
    if format == 'html':
        return fig.to_html()
    elif format == 'png':
        return fig.to_image(format='png')
    else:
        return 'Invalid format', 400
if __name__ == '__main__':
    app.run()