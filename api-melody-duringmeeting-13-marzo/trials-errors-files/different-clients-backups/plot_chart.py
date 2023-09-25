import json
import requests

def plotChart1(variable_names, data):
  """
  Plots a chart of the data.

  Args:
    variable_names: A list of the variable names.
    data: The data to plot.

  Returns:
    A JSON object containing the chart data.
  """

  if len(variable_names) < 2:
    raise ValueError("Query must return at least two variables")

  url = "https://quickchart.io/api/chart"
  payload = {
    "data": {
      "labels": variable_names,
      "datasets": [{"data": {"values": list(data)}}]
    },
    "type": "bar",
  }

  response = requests.post(url, data=payload)
  if response.status_code != 200:
    raise ValueError(f"Error from QuickChart: {response.status_code}")

  return json.loads(response.content)


if __name__ == "__main__":
  variable_names = ["alias", "count"]
  data = [
    1,
    2,
    3,
    4,
    5,
  ]

  chart_data = plotChart1(variable_names, data)
