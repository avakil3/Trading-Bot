from lumibot.brokers import Alpaca

# from lumibot.backtesting import YahooDataBacktesting
from lumibot.backtesting import BacktestingBroker, PolygonDataBacktesting
from lumibot.traders import Trader
from lumibot.strategies.strategy import Strategy
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from decouple import config
import json


ALPACA_CONFIG = {
    # Put your own Alpaca key here:
    "API_KEY": config("ALPACA_API_KEY"),
    # Put your own Alpaca secret here:
    "API_SECRET": config("ALPACA_API_SECRET"),
    "PAPER": True,
}


class MLTrader(Strategy):

    parameters = {"symbol": "AAPL", "cash_at_risk": 0.1}

    def initialize(self):
        self.symbol = self.get_parameters()["symbol"]
        # self.sleeptime = "24H"
        self.sleeptime = "1M"
        # Will make on_trading_iteration() run every 180 minutes
        # self.sleeptime = "180M"
        self.last_trade = None
        self.cash_at_risk = self.get_parameters()["cash_at_risk"]
        self.take_profit_percentage = 0.1
        self.stop_loss_percentage = 0.05

        # Opening JSON file
        f = open("RSI_data_2024-03.json")
        # returns JSON object as
        # a dictionary
        self.RSI_data = json.load(f)
        self.RSI_data = self.RSI_data["Technical Analysis: RSI"]
        self.last_order = "sell"

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def on_trading_iteration(self):
        date_time = self.get_datetime()
        get_indicator_values(date_time)
        # if date_time not in self.RSI_data:
        #     return  # DO NOTHING

        RSI_val = float(self.RSI_data[date_time]["RSI"])

        if RSI_val < 30:

            cash, last_price, quantity = self.position_sizing()
            print("\n")
            print(date_time, last_price)

            if cash > last_price and self.last_order == "sell":
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    # take_profit_price=last_price * (1 + self.take_profit_percentage),
                    stop_loss_price=last_price * (1 - self.stop_loss_percentage),
                    time_in_force="day",
                )
                self.submit_order(order)
                self.last_order = "buy"
                print(f"----------------MADE A TRADE-----------")
                print("RSI", RSI_val)
                print("DATE: " + date_time)

        elif RSI_val > 65 and self.last_order == "buy":
            print(f"----------------SOLD POSITION-----------")
            print("RSI", RSI_val)
            print("DATE: " + date_time)
            self.sell_all()
            self.last_order = "sell"

    def get_indicator_values(self):
        
# trader = TradingClient(
#     ALPACA_CONFIG.get("API_KEY"),
#     ALPACA_CONFIG.get("API_SECRET"),
#     paper=True,
# )


# broker = Alpaca(ALPACA_CONFIG)

# strategy = MLTrader(
#     name="mlstrat",
#     broker=broker,
# )
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()


# # preparing order data
# market_order_data = MarketOrderRequest(
#     symbol="SPY", qty=0.1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
# )

# # Market order
# market_order = trading_client.submit_order(order_data=market_order_data)


def backtesting():
    start_date = datetime(2024, 3, 1)
    end_date = datetime(2024, 3, 2)

    polygon_data_source = PolygonDataBacktesting(
        datetime_start=start_date,
        datetime_end=end_date,
        api_key=config("POLYGON_API_KEY"),
        has_paid_subscription=False,  # Set this to True if you have a paid subscription to polygon.io (False assumes you are using the free tier)
    )
    broker = BacktestingBroker(polygon_data_source)
    strategy = MLTrader(
        name="mlstrat",
        broker=broker,
    )
    trader = Trader(backtest=True)
    trader.add_strategy(strategy)
    trader.run_all()

    # strategy.backtest(polygon_data_source, start_date, end_date, benchmark_asset="SPY")


if __name__ == "__main__":
    backtesting()
