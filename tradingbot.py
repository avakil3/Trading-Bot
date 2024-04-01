from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.traders import Trader
from lumibot.strategies.strategy import Strategy
from datetime import datetime

from alpaca.trading.client import TradingClient

from creds import ALPACA_CONFIG


class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        # Will make on_trading_iteration() run every 180 minutes
        # self.sleeptime = "180M"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.take_profit_percentage = 0.1
        self.stop_loss_percentage = 0.05

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()

        if cash > last_price and self.last_trade == None:
            order = self.create_order(
                self.symbol,
                quantity,
                "buy",
                type="bracket",
                take_profit_price=last_price * (1 + self.take_profit_percentage),
                stop_loss_price=last_price * (1 - self.stop_loss_percentage),
            )
            self.submit_order(order)
            self.last_trade = "buy"


broker = Alpaca(ALPACA_CONFIG)
strategy = MLTrader(
    name="mlstrat", broker=broker, parameters={"symbol": "SPY", "cash_at_risk": 0.5}
)

start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)

trading_client = TradingClient(
    ALPACA_CONFIG.get("API_KEY"), ALPACA_CONFIG.get("API_SECRET")
)

print(trading_client.get_account().account_number)
# strategy.backtest(YahooDataBacktesting, start_date, end_date, parameters={})
