import logging        
from client import Client
import datetime
from dataclasses import dataclass

@dataclass
class schwabOrder:
    orderType: str = "LIMIT"
    session: str = "NORMAL"
    duration: str = "DAY"
    strategy: str = "SINGLE"
    price: float = 0.0
    ticker:str = ""
    qty: float = 0.0
    buySell : str = "BUY"


class OrderHandler(object):

    @staticmethod
    def getAccs(client, verbose:bool = True):
        if verbose:
            logging.info("\nGet account number and hashes for linked accounts")
        linked_accounts = client.account_linked().json()
        if verbose:
            logging.info(linked_accounts)
        account_hash = linked_accounts[0].get('hashValue') # this will get the first linked account
        return linked_accounts, account_hash
    
    @staticmethod
    def getAccDetails(client, account_hash):
        logging.info("\nGet details for all linked accounts")
        logging.info(client.account_details_all().json())

        logging.info("\nGet specific account positions (uses default account, can be changed)")
        accDetails = client.account_details(account_hash, fields="positions").json()
        logging.info(accDetails)
        return accDetails

    @staticmethod
    def getAccOrders(client, account_hash):
        _, account_hash = OrderHandler.getAccs(client, False)
        # get orders for a linked account
        logging.info("\nGet orders for a linked account")
        orders = client.account_orders(account_hash, datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30), datetime.datetime.now(datetime.timezone.utc)).json()
        logging.info(orders)
        return orders
    
    @staticmethod
    def placeOrder(client, account_hash, order: schwabOrder):
        # place an order, get the details, then cancel it (uncomment to test)
        order = {"orderType": order.orderType,
                "session": order.session,
                "duration": order.duration,
                "orderStrategyType": order.strategy,
                "price": order.price,
                "orderLegCollection": [
                    {"instruction": order.buySell,
                    "quantity": order.qty,
                    "instrument": {"symbol": order.ticker,
                                    "assetType": "EQUITY" ## need a mapping for this
                                    }
                    }
                ]
                }
        resp = client.order_place(account_hash, order)
        logging.info("\nPlace an order:")
        logging.info(f"Response code: {resp}")
        # get the order ID - if order is immediately filled then the id might not be returned
        order_id = resp.headers.get('location', '/').split('/')[-1]
        logging.info(f"Order id: {order_id}")
        return resp