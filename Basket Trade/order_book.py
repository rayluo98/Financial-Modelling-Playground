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
        history.columns=["Date", "CostBasis", "Value", "PnL"]
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
        books.columns=["Date", "Ticker", "Quantity", "CostBasis", "Value", "Unrealized PnL"]
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
    def backfillPnL(self, price_history: pd.DataFrame)->None:
        # might need rename here
        price_history.columns=["Date", "Ticker", "Price"]
        orderBook = Book.get_books()
        orderBook.sort_values("Date", ascending=False, inplace=True)
        price_history.sort_values("Date", ascending=False, inplace=True)
        correctedOrders = pd.merge_asof(price_history, orderBook, on="Date", by=["Ticker"])
        correctedOrders["Value"] = correctedOrders.apply(lambda dr: dr["Price"] * dr["Quantity"], axis=1)
        correctedOrders["Unrealized PnL"] = correctedOrders["Value"] - correctedOrders["Cost Basis"]
        correctedOrders =correctedOrders.filter(["Date", "Ticker", "CostBasis", "Value", "Unrealized PnL"])
        self.history = correctedOrders.groupby("Date").agg(CostBasis=("CostBasis", "sum"),
                                                           Value=("Value", "sum"),
                                                           PnL = ("Unrealized PnL", "sum"))
    
        