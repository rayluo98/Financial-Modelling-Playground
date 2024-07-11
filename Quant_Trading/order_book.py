import pandas as pd
from dataclasses import dataclass, asdict

@dataclass
class Page:
    Date:pd.Timestamp
    Ticker:str
    Quantity:float
    CostBasis:float
    MV:float
    UnrealizedPnL:float
    Cash:float
    
    def __init__(self, date: pd.Timestamp, stock_name:str, quantity: float = 0.0, costbasis: float =0.0, mv: float=0.0, cash:float=0.0, unrealizedpnl: float=0.0):
        self.Ticker = stock_name
        self.Date = date
        self.Quantity = quantity
        self.CostBasis = costbasis
        self.MV = mv
        self.Cash = cash
        self.UnrealizedPnL = unrealizedpnl

@dataclass
class Trade:
    Date: pd.Timestamp
    Ticker: str
    Price: float 
    Quantity: float
    Longshort: bool
    def __init__(self, date: pd.Timestamp, stock_name: str, current_price: float = 0.0, quantity: float = 0):
        self.Ticker = stock_name
        self.Price = current_price
        self.Quantity = quantity
        self.Longshort = quantity > 0
        self.Date = date
        
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
    '''
    orders: List[Trade]
    history: pd.DataFrame
    books: List[Page]
    cash: pd.DataFrame() 
    verbose: bool
    '''

    def __init__(self):
        self.orders:list[Trade]=list()
        self.history:list=list()
        self.books:list[Page]=list()
        self.cash = pd.DataFrame()
        self.verbose = False
    
    def verbose(cls, on:bool=True)->None:
        cls.verbose = on
    # returns a list of orders 
   
    def get_books(cls):
        if len(cls.books)==0:
            return pd.DataFrame(columns=["Date", "Ticker", "Quantity", "CostBasis", "Value", "Cash", "UnrealizedPnL"])
        books = pd.json_normalize(asdict(obj) for obj in cls.books)
        return books

    def getOrderDf(cls):
        return pd.json_normalize(asdict(obj) for obj in cls.orders)
    
    def getHistoryDf(cls):
        history = pd.DataFrame(cls.history)
        return history

    def get_orders(cls):
        return cls.orders

    # order history
    def get_history(cls):
        return cls.history

    def get_pnl_snapshot(cls, start_date: pd.Timestamp=None, end_date: pd.DataFrame=None)->pd.DataFrame:
        hist = cls.getHistoryDf()
        if start_date == None:
            return hist.iloc[-1,:]
        else:
            return hist[start_date:end_date,:]

    def getTickerBook(cls, ticker: list[str], start_date:pd.DataFrame= None, end_date:pd.DataFrame=None)->pd.DataFrame:
        book = cls.get_books()
        ## if first entry we return an empty book
        if (book.shape[0]==0):
            return book
        if start_date==None:
            return book[book['Ticker'].isin(ticker)].tail(1)
        else:
            return book[(book['Ticker'].isin(ticker)) & (book['Ticker'] <= end_date) & (book['Ticker'] >= start_date)]
    
    # currently assume that orders are executed 100% of the time
    # tca = transaction cost
    def addOrder(cls, date:pd.Timestamp, ticker:str, price: float, qty:float, tca: float = 0)->None:
        order = Trade(date, ticker, price, qty)
        cost = price*qty
        ## update cash according to order
        new_cash  = -1*(tca+cost)
        lastBook = cls.getTickerBook([ticker])
        if (lastBook.shape[0] ==0): 
            new_mv = qty*price
            new_cost = cost
            new_qty = qty
        else:
            new_mv = (lastBook.iloc[0].at['Quantity'] + qty)*price
            new_cost = lastBook.iloc[0].at['CostBasis'] + cost
            new_qty = lastBook.iloc[0].at['Quantity'] + qty
            new_cash = lastBook.iloc[0].at['Cash'] - (tca + cost)
        cls.orders.append(order)      
        cls.books.append(Page(date,  ticker, new_qty, new_mv, new_mv, new_cash, new_mv - new_cost))
        cls.history.append({"Date":date,"Ticker":ticker,"Quantity": new_qty,
                            "CostBasis": new_cost, "Value":new_mv, "PnL": new_mv - new_cost, "Cash": new_cash})
        
    # we repopulate pnl using price history of stocks
    def backfillPnL(cls, price_history: pd.DataFrame)->None:
        # might need rename here
        # ["Date", "Ticker", "Price"]
        orderBook = cls.get_books()
        if orderBook.shape[0]==0:
            return price_history
        orderBook.sort_values("Date", ascending=True, inplace=True)
        price_history.sort_values("Date", ascending=True, inplace=True)
        correctedOrders = pd.merge_asof(price_history, orderBook, on="Date", by=["Ticker"])
        correctedOrders["Value"] = correctedOrders.apply(lambda dr: dr["Price"] * dr["Quantity"], axis=1)
        correctedOrders["UnrealizedPnL"] = correctedOrders["Value"] - correctedOrders["CostBasis"]
        correctedOrders.to_csv(r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Basket Trade\debug.csv')
        correctedOrders =correctedOrders.filter(["Date", "Ticker", "CostBasis", "Value", "UnrealizedPnL", "Cash"])
        cls.history = correctedOrders.groupby("Date").agg(CostBasis=("CostBasis", "sum"),
                                                           Value=("Value", "sum"),
                                                           PnL = ("UnrealizedPnL", "sum"),
                                                           Cash = ("Cash","sum"))
        cls.history["PnL"] += cls.history["Cash"]
    
        