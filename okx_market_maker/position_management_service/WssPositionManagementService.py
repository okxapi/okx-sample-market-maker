import time
from typing import List, Dict
import copy

from okx_market_maker.position_management_service.model.BalanceAndPosition import BalanceAndPosition, \
    BalanceData, PosData
from okx_market_maker.position_management_service.model.Account import Account, AccountDetail
from okx_market_maker.position_management_service.model.Positions import Position, Positions
from okx.websocket.WsPrivate import WsPrivate
from okx_market_maker import balance_and_position_container, account_container, positions_container
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE


class WssPositionManagementService(WsPrivate):
    def __init__(self, url: str, api_key: str = API_KEY, passphrase: str = API_PASSPHRASE,
                 secret_key: str = API_KEY_SECRET, useServerTime: bool = False):
        super().__init__(api_key, passphrase, secret_key, url, useServerTime)
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

    @staticmethod
    def _prepare_args() -> List[Dict]:
        args = []
        account_sub = {
                "channel": "account"
        }
        args.append(account_sub)
        positions_sub = {
            "channel": "positions",
            "instType": "ANY"
        }
        args.append(positions_sub)
        balance_and_position_sub = {
            "channel": "balance_and_position"
        }
        args.append(balance_and_position_sub)
        return args


def _callback(message):
    arg = message.get("arg")
    # print(message)
    if not arg or not arg.get("channel"):
        return
    if message.get("event") == "subscribe":
        return
    if arg.get("channel") == "balance_and_position":
        on_balance_and_position(message)
        # print(balance_and_position_container)
    if arg.get("channel") == "account":
        # print(message)
        on_account(message)
        # print(account_container)
    if arg.get("channel") == "positions":
        # print(message)
        on_position(message)
        # print(positions_container)


def on_balance_and_position(message):
    if not balance_and_position_container:
        balance_and_position_container.append(BalanceAndPosition.init_from_json(message))
    else:
        balance_and_position_container[0].update_from_json(message)


def on_account(message):
    if not account_container:
        account_container.append(Account.init_from_json(message))
    else:
        account_container[0].update_from_json(message)


def on_position(message):
    if not positions_container:
        positions_container.append(Positions.init_from_json(message))
    else:
        positions_container[0].update_from_json(message)


if __name__ == "__main__":
    url = "wss://ws.okx.com:8443/ws/v5/private"
    position_management_service = WssPositionManagementService(url=url)
    position_management_service.start()
    position_management_service.run_service()
    time.sleep(30)
