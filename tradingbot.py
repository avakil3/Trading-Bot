from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.traders import Trader
from lumibot.strategies.strategy import Strategy
from datetime import datetime

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from creds import ALPACA_CONFIG


class MLTrader(Strategy):

    parameters = {"symbol": "AAPL", "cash_at_risk": 0.5}

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

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def on_trading_iteration(self):
        print(self.get_datetime(), self.get_last_price("AAPL"))
        # cash, last_price, quantity = self.position_sizing()

        # if cash > last_price:
        #     order = self.create_order(
        #         self.symbol,
        #         quantity,
        #         "buy",
        #         type="bracket",
        #         take_profit_price=last_price * (1 + self.take_profit_percentage),
        #         stop_loss_price=last_price * (1 - self.stop_loss_percentage),
        #         # time_in_force='day'
        #     )
        #     self.submit_order(order)
        #     self.last_trade = "buy"


# trader = TradingClient(
#     ALPACA_CONFIG.get("API_KEY"),
#     ALPACA_CONFIG.get("API_SECRET"),
#     paper=True,
# )


broker = Alpaca(ALPACA_CONFIG)

strategy = MLTrader(
    name="mlstrat",
    broker=broker,
)
# trader = Trader()
# trader.add_strategy(strategy)
# trader.run_all()


# # preparing order data
# market_order_data = MarketOrderRequest(
#     symbol="SPY", qty=0.1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY
# )

# # Market order
# market_order = trading_client.submit_order(order_data=market_order_data)


start_date = datetime(2024, 4, 1)
end_date = datetime(2024, 4, 2)
strategy.backtest(YahooDataBacktesting, start_date, end_date, benchmark_asset="SPY")
