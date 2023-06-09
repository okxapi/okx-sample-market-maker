import json
import time
from typing import List, Dict

from okx_market_maker.order_management_service.model.Order import Order, Orders
from okx.websocket.WsPrivate import WsPrivate
from okx_market_maker import orders_container
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE


class WssOrderManagementService(WsPrivate):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
        self.args = []

    def run_service(self):
        args = self._prepare_args()
        print(args)
        print("subscribing")
        orders_container.append(Orders())
        self.subscribe(args, _callback)
        self.args += args

    def stop_service(self):
        self.unsubscribe(self.args, lambda message: print(message))
        self.close()

    @staticmethod
    def _prepare_args() -> List[Dict]:
        args = []
        orders_sub = {
            "channel": "orders",
            "instType": "ANY",
        }
        args.append(orders_sub)
        return args


def _callback(message):
    arg = message.get("arg")
    # print(message)
    if not arg or not arg.get("channel"):
        return
    if message.get("event") == "subscribe":
        return
    if arg.get("channel") == "orders":
        on_orders_update(message)
        # print(orders_container)


def on_orders_update(message):
    if not orders_container:
        orders_container.append(Orders.init_from_json(message))
    else:
        orders_container[0].update_from_json(message)


if __name__ == "__main__":
    # url = "wss://ws.okx.com:8443/ws/v5/private"
    url = "wss://ws.okx.com:8443/ws/v5/private?brokerId=9999"
    order_management_service = WssOrderManagementService(url=url)
    order_management_service.start()
    order_management_service.run_service()
    time.sleep(30)
