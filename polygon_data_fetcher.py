from decouple import config
import requests
import json

symbol = "AAPL"

timespan = "hour"
function = "macd"
# function = "rsi"

url = f"https://api.polygon.io/v1/indicators/{function}/{symbol}?timespan={timespan}&adjusted=true&short_window=12&long_window=26&signal_window=9&series_type=close&order=desc&apiKey={config('POLYGON_API_KEY')}&limit=5000&date.gte=2024-03-01&date.lte=2023-04-01"

r = requests.get(url)
data = r.json()

# store data
with open(f"polygon_{function}_{timespan}_data.json", "w") as f:
    formatted_data = {}
    for interval in data["results"]["values"]:
        formatted_data[interval["timestamp"]] = interval
    json.dump(formatted_data, f)
