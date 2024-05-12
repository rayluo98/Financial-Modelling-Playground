import pandas as pd
from dataclasses import dataclass

@dataclass
class Page:
    Date: pd.DateTime
    Ticker: str
    Quantity: float
    CostBasis: float
    MV: float, 
    unrealizedPnl: float

@dataclass
class Trade:
    def __init__(self, date: pd.Timestamp, stock_name: str, current_price: float = 0.0, quantity: str = 0):
        self.stock = stock_name
        self.price = current_price
        self.quantity = quantity
        self.long_short = quantity > 0
        self.date = date
        
    def info(self):
        dir = "long" if self.long_short else "short"
        return [self.date, self.stock, self.price, self.quantity, dir]
        
    def cur_pnl(self, current_price):
        if self.long_short:
            profit = (current_price-self.price)*self.quantity
            return profit
        else:
            profit = (self.price-current_price)*self.quantity
            return profit
        
## might create class for exchange specific trade
class Book:
    def __init__(self):
        self.orders: Trade = []
        self.history: pd.DataFrame = pd.DataFrame()
        self.books: list = []
        self.cash: float = True
        self.verbose: bool = False

    def verbose(self, on:bool=True)->None:
        self.verbose = on
    # returns a list of orders 
    @classmethod   
    def positions(self):
        return self.orders
    # order history
    @classmethod
    def get_history(self):
        history = pd.DataFrame(self.history)
        history.columns=["Date", "Cost Basis", "Value", "PnL"]
        return history
    @classmethod
    def get_pnl_snapshot(start_date: pd.Datetime=None, end_date: pd.DateFrame=None)->pd.DataFrame:
        hist = Book.get_history()
        if start_date == None:
            return hist.iloc[-1]
        else:
            return hist[start_date:end_date]
    @classmethod
    def get_books(self):
        books = pd.DataFrame(self.books)
        books.columns=["Date", "Ticker", "Quantity", "Cost Basis", "Value", "Unrealized PnL"]
        return books
    @classmethod
    def getTickerBook(ticker: list[str], start_date:pd.DataFrame= None, end_date:pd.DataFrame=None)->pd.DataFrame:
        book = Book.get_books()
        if start_date==None:
            return book[book['Ticker'].isin(ticker)].iloc[-1]
        else:
            return book[book['Ticker'].isin(ticker)][start_date:end_date]
    
    # currently assume that orders are executed 100% of the time
    # tca = transaction cost
    @classmethod
    def addOrder(self, date:pd.DateTime, ticker:str, price: float, qty:float, tca: float = 0)->None:
        self.cash -= tca
        order = Trade(date, ticker, price, qty)
        cost = price*qty
        lastBook = Book.getTickerBook([ticker])
        new_mv = (lastBook['Quantity'] + qty)*price
        new_cost = lastBook["Cost Basis"] + cost
        self.cash -= cost
        self.orders.append(date, ticker, lastBook["Quantity"] + qty, new_cost, new_mv, new_mv - new_cost)
        self.history.append(date, new_cost, new_mv, new_mv - new_cost)

    # we repopulate pnl using price history of stocks
    @classmethod
    def backfillPnL(price_history: pd.DataFrame):


    def long(self, stock_name, current_price, dollar_amount):
        order = Trade(stock_name, current_price[stock_name], dollar_amount, True)
        self.orders.append(order)
        self.history.append(order.info())
        
    def short(self, stock_name, current_price, dollar_amount):
        order = Trade(stock_name, current_price[stock_name], dollar_amount, False)
        self.orders.append(order)
        self.history.append(order.info())

    def cur_pnl(self, price):
        pnls = []
        cur_price = []
        for pos in self.orders:
            pnls.append(pos.cur_pnl(price[pos.stock]))
            cur_price.append(price[pos.stock])
        return [pnls, cur_price, sum(pnls)]
    def get_pnl_history(self):
        df = pd.DataFrame(self.pnl_history)
        df.columns = ['Stock', 'Open Price', 'Quantity', 'Long/Short', 'Close Price', 'PnL']
        return df
        
    def sell_all(self, price): 
        for pos in self.orders:
            profit = pos.cur_pnl(price[pos.stock])
            dir = 'long' if pos.long_short else 'short'
            res = [pos.stock, pos.price, pos.quantity, dir, price[pos.stock], profit]
            self.pnl_history.append(res)
        cur_pnl = self.cur_pnl(price)[2]
        self.profit.append(cur_pnl)
        self.cumulative_profit += cur_pnl
        self.orders = []
        return
        