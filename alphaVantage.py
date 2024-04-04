# from creds import ALPHA_VANTAGE_KEY
import requests
import json
from decouple import config


# INPUTS
symbol = "AAPL"
interval = "1min"
month = "2024-03"
function = "RSI"


def get_data(symbol, interval, function, month=None):
    url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&interval={interval}&time_period=14&series_type=close&apikey={(config('ALPHA_VANTAGE_KEY'))}&datatype=json{f'&month={month}' if month else ''}"
    r = requests.get(url)
    data = r.json()

    # store data
    with open(f"{function}_data_{month}.json", "w") as f:
        json.dump(data, f)


get_data(symbol, interval, function)
