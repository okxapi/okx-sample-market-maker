import threading
from typing import Dict, List
import time
from okx_market_maker import order_books
from okx_market_maker.market_data_service.model.OrderBook import OrderBook, OrderBookLevel
from okx.websocket.WsPublic import WsPublic


class WssMarketDataService(WsPublic):
    def __init__(self, url, inst_id, channel="books5"):
        super().__init__(url)
        self.inst_id = inst_id
        self.channel = channel
        order_books[self.inst_id] = OrderBook(inst_id=inst_id)
        self.args = []

    def run_service(self):
        args = self._prepare_args()
        print(args)
        print("subscribing")
        self.subscribe(args, _callback)
        self.args += args

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: print(message))
        self.close()

    def _prepare_args(self) -> List[Dict]:
        args = []
        books5_sub = {
            "channel": self.channel,
            "instId": self.inst_id
        }
        args.append(books5_sub)
        return args


def _callback(message):
    arg = message.get("arg")
    # print(message)
    if not arg or not arg.get("channel"):
        return
    if message.get("event") == "subscribe":
        return
    if arg.get("channel") in ["books5", "books", "bbo-tbt", "books50-l2-tbt", "books-l2-tbt"]:
        on_orderbook_snapshot_or_update(message)
        # print(order_books)


def on_orderbook_snapshot_or_update(message):
    """
    :param message:
    {
    "arg": {
        "channel": "books",
        "instId": "BTC-USDT"
    },
    "action": "snapshot",
    "data": [{
        "asks": [
            ["8476.98", "415", "0", "13"],
            ["8477", "7", "0", "2"],
            ["8477.34", "85", "0", "1"],
            ["8477.56", "1", "0", "1"],
            ["8505.84", "8", "0", "1"],
            ["8506.37", "85", "0", "1"],
            ["8506.49", "2", "0", "1"],
            ["8506.96", "100", "0", "2"]
        ],
        "bids": [
            ["8476.97", "256", "0", "12"],
            ["8475.55", "101", "0", "1"],
            ["8475.54", "100", "0", "1"],
            ["8475.3", "1", "0", "1"],
            ["8447.32", "6", "0", "1"],
            ["8447.02", "246", "0", "1"],
            ["8446.83", "24", "0", "1"],
            ["8446", "95", "0", "3"]
        ],
        "ts": "1597026383085",
        "checksum": -855196043
    }]
}
    :return:
    """
    arg = message.get("arg")
    inst_id = arg.get("instId")
    action = message.get("action")
    if inst_id not in order_books:
        order_books[inst_id] = OrderBook(inst_id=inst_id)
    data = message.get("data")[0]
    if data.get("asks"):
        if action == "snapshot" or not action:
            ask_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["asks"]]
            order_books[inst_id].set_asks_on_snapshot(ask_list)
        if action == "update":
            for level_info in data["asks"]:
                order_books[inst_id].set_asks_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("bids"):
        if action == "snapshot" or not action:
            bid_list = [OrderBookLevel(price=float(level_info[0]),
                                       quantity=float(level_info[1]),
                                       order_count=int(level_info[3]),
                                       price_string=level_info[0],
                                       quantity_string=level_info[1],
                                       order_count_string=level_info[3],
                                       ) for level_info in data["bids"]]
            order_books[inst_id].set_bids_on_snapshot(bid_list)
        if action == "update":
            for level_info in data["bids"]:
                order_books[inst_id].set_bids_on_update(
                    OrderBookLevel(price=float(level_info[0]),
                                   quantity=float(level_info[1]),
                                   order_count=int(level_info[3]),
                                   price_string=level_info[0],
                                   quantity_string=level_info[1],
                                   order_count_string=level_info[3],
                                   )
                )
    if data.get("ts"):
        order_books[inst_id].set_timestamp(int(data["ts"]))
    if data.get("checksum"):
        order_books[inst_id].set_exch_check_sum(data["checksum"])


class ChecksumThread(threading.Thread):
    def __init__(self, wss_mds: WssMarketDataService):
        self.wss_mds = wss_mds
        super().__init__()

    def run(self) -> None:
        while 1:
            try:
                for inst_id, order_book in order_books.items():
                    order_book: OrderBook
                    if order_book.do_check_sum():
                        continue
                    self.wss_mds.stop_service()
                    time.sleep(3)
                    self.wss_mds.run_service()
                    break
                time.sleep(5)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    # url = "wss://ws.okx.com:8443/ws/v5/public"
    url = "wss://ws.okx.com:8443/ws/v5/public?brokerId=9999"
    market_data_service = WssMarketDataService(url=url, inst_id="BTC-USDT-SWAP", channel="books")
    market_data_service.start()
    market_data_service.run_service()
    check_sum = ChecksumThread(market_data_service)
    check_sum.start()
    time.sleep(30)

