from decouple import config
import requests
import json

url = "https://api.taapi.io/bulk"

headers = {"Content-Type": "application/json"}


def get_current_data(symbol, interval):

    payload = {
        "secret": config("TAAPI_API_KEY"),
        "construct": {
            "type": "stocks",
            "symbol": symbol,
            "interval": interval,
            "indicators": [
                {"indicator": "rsi"},
                {"indicator": "macd"},
            ],
        },
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if response.status_code != 200:
        return response.json()

    data = response.json()["data"]

    result = {}
    for indicator in data:
        result[indicator["indicator"]] = indicator["result"]

    # print(result)
    return result
