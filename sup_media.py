import pandas as pd
from dateutil import relativedelta
import datetime
import pandas_datareader as pdr
#import pandas_ta as ta
import datetime as dt
from stockstats import StockDataFrame
from matplotlib.figure import Figure
from io import BytesIO
import base64


class SupMedia:
    ''' This strategy checks if closing price of the ticker (SPY) is above EMA10 and returns BUY or SELL if below.'''

    def __init__(self, ticker):
        today = datetime.date.today()
        end_year = today.year
        end_month = today.month

        # start = dt.datetime(start_year, start_month, 1)
        start = dt.datetime(2019, 1, 1)
        end = dt.datetime(end_year, end_month, 1)
        yahoo_df = pdr.get_data_yahoo(ticker, start, end, interval="m")
        stock_data = StockDataFrame.retype(yahoo_df)
        self.stock_info = stock_data[~stock_data.index.duplicated(keep="first")][:-1]
        self.ticker_name = ticker

    def get_last_closing_price(self):
        ticker_close = self.stock_info.close.iloc[-1]
        return ticker_close

    def get_last_sma10(self):
        ticker_sma_10 = self.stock_info["close_10_sma"].iloc[-1]
        return ticker_sma_10

    def take_action(self):
        last_price = self.get_last_closing_price()
        last_sma10 = self.get_last_sma10()
        if last_price > last_sma10:
            action = "BUY"
        else:
            action = "SELL"
        return action

    def last_date(self):
        last_month_date = self.stock_info.index[-1].date()
        return last_month_date

    def get_tendency_change_date(self):
        n = 0
        for stock_entry in self.stock_info.index[::-1]:
            try:
                if self.stock_info.close[stock_entry] > self.stock_info["close_10_sma"][stock_entry]:
                    tendency_change_date = stock_entry.date()
                    n = n + 1
                else:
                    if n != 0:
                        tendency_change_date = stock_entry.date() + pd.DateOffset(months=1)
                    else:
                        tendency_change_date = "Tendency Down"
                break
            except ValueError:
                tendency_change_date = "There was an error retrieving tendency change date"
        return tendency_change_date

    def get_profit(self):
        last_price = self.get_last_closing_price()
        tendency_price_change = 0
        for date in self.stock_info.index[::-1]:
            if self.stock_info.close[date] > self.stock_info["close_10_sma"][date]:
                tendency_price_change = self.stock_info.close[date]
            else:
                break
        if tendency_price_change:
            profit = last_price - tendency_price_change
        else:
            profit = 0.0
        return profit

    def get_tendency_months(self):
        n = 0
        for date in self.stock_info.index[::-1]:
            if self.stock_info.close[date] > self.stock_info["close_10_sma"][date]:
                n = n + 1
            else:
                break
        return n

    def display_graph(self):
        # Generate the figure without using pyplot
        fig = Figure()
        ax = fig.subplots(sharey=True, sharex=True)
        #ax.axes.set_ylim(1000, 6000)
        #ax.invert_xaxis()
        ax.plot(self.stock_info.close[-10:])
        ax.plot(self.stock_info["close_10_sma"][-10:])
        fig.autofmt_xdate(rotation=45)
        fig.legend(["PRICE", "SMA_10"])
        buf = BytesIO()
        fig.savefig(buf, format="png", transparent=True)
        graph = base64.b64encode(buf.getbuffer()).decode("ascii")
        return graph

    def get_ticker_name(self):
        return self.ticker_name