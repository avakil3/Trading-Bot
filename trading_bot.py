from lumibot.brokers import Alpaca
import pandas as pd
from lumibot.backtesting import BacktestingBroker, PolygonDataBacktesting
from lumibot.traders import Trader
from lumibot.strategies.strategy import Strategy
from datetime import datetime, timedelta

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
        self.sleeptime = "30M"
        # Will make on_trading_iteration() run every 180 minutes
        # self.sleeptime = "180M"
        self.last_trade = None
        self.cash_at_risk = self.get_parameters()["cash_at_risk"]
        self.take_profit_percentage = 0.1
        self.stop_loss_percentage = 0.05
        self.RSI_df = self.get_backtest_data("polygon_rsi_hour_data.json")
        self.MACD_df = self.get_backtest_data("polygon_macd_hour_data.json")

        self.last_order = "sell"

    def get_backtest_data(self, file_name):
        RSI_json = json.load(open(file_name))
        # Convert JSON to DataFrame
        df = pd.DataFrame.from_dict(RSI_json, orient="index")[::-1]
        # Reset index to make timestamp a column
        df.reset_index(inplace=True)
        del df["timestamp"]  # duplicate column
        df.rename(columns={"index": "timestamp"}, inplace=True)
        return df

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def get_indicators(self, date_time, backTest):
        if backTest:
            # Edit the format of the Timestamp to match with backtest data
            cur_ts = str(datetime.timestamp(date_time))[:-2] + "000"
            # Retrieve CURRENT RSI data
            cur_rsi = self.RSI_df.loc[self.RSI_df.timestamp == cur_ts]
            # Retrieve CURRENT MACD data
            cur_macd = self.MACD_df.loc[self.MACD_df.timestamp == cur_ts]

            cur_rsi = self.RSI_df.loc[self.RSI_df.timestamp == cur_ts]

            # Retrieve PAST PERIOD's indicator data
            prev_rsi = self.RSI_df.loc[cur_rsi.index - 1]
            prev_macd = self.MACD_df.loc[cur_macd.index - 1]

            return cur_rsi, cur_macd, prev_rsi, prev_macd

        # real time trading here
        # make API calls here

    def on_trading_iteration(self):

        date_time = self.get_datetime()
        if date_time.minute == 30:  # SKIP THE HALF HOURS
            return

        cur_rsi, cur_macd, prev_rsi, prev_macd = self.get_indicators(
            date_time, backTest=True
        )

        if cur_rsi.empty or cur_macd.empty or prev_rsi.empty or prev_macd.empty:
            print("INDICATOR DATA NOT FOUND: SKIPPING TRADE ITERATION")
            return
        """
        1. cur RSI < 30
        2. curMACD < 0 and  curMACD.value > curMACD.signal
        3. prevMACD.value < prevMACD.signal
        """

        # print("cur_rsi.value < 30: ", cur_rsi.value < 30)
        # print("cur_macd.value < 0: ", cur_macd.value < 0)
        # print("cur_macd.value > cur_macd.signal: ", cur_macd.value > cur_macd.signal)
        # print("prev_macd.value < cur_macd.signal:  ", prev_macd.value < cur_macd.signal)
        # BUY SIGNAL
        # print(
        #     cur_rsi.value < 30,
        #     cur_macd.value < 0,
        #     cur_macd.value > cur_macd.signal,
        #     prev_macd.value < cur_macd.signal,
        # )
        print(prev_macd.value)
        print(cur_macd.signal)
        print(prev_macd.value < cur_macd.signal)

        if (
            cur_rsi.value < 30
            and cur_macd.value < 0
            and cur_macd.value > cur_macd.signal
            and prev_macd.value < cur_macd.signal
        ):

            print("HEREEEE")
            cash, last_price, quantity = self.position_sizing()

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
                print("RSI", cur_rsi.value)
                print("DATE: " + date_time)

        elif (
            cur_rsi.value > 70
            or cur_macd.histogram < 0
            or (cur_macd.value < cur_macd.signal and prev_macd.value > prev_macd.signal)
            and self.last_order == "buy"
        ):
            """
            SELL STRATEGY
            1. RSI value > 70
            2. MACD histogram < 0
            3. curMACD value < cur MACD Signal AND prevMACD value > prev MACD signal
            """
            print(f"----------------SOLD POSITION-----------")
            print("RSI", cur_rsi.value)
            print("DATE: " + date_time)
            self.sell_all()
            self.last_order = "sell"


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
    end_date = datetime(2024, 3, 10)

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


if __name__ == "__main__":
    backtesting()
