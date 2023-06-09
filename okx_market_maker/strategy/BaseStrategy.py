import time
import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import logging

from okx.Status import StatusAPI
from okx_market_maker.market_data_service.model.Instrument import Instrument, InstState
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.position_management_service.model.Positions import Positions
from okx_market_maker.strategy.params.ParamsLoader import ParamsLoader
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.order_management_service.model.OrderRequest import PlaceOrderRequest, \
    AmendOrderRequest, CancelOrderRequest
from okx.Trade import TradeAPI
from okx_market_maker.settings import *
from okx_market_maker import orders_container, order_books, account_container, positions_container, tickers_container
from okx_market_maker.strategy.model.StrategyOrder import StrategyOrder, StrategyOrderStatus
from okx_market_maker.strategy.model.StrategyMeasurement import StrategyMeasurement
from okx_market_maker.market_data_service.model.OrderBook import OrderBook
from okx_market_maker.position_management_service.model.Account import Account
from okx_market_maker.order_management_service.model.Order import Orders, Order, OrderState, OrderSide
from okx_market_maker.strategy.risk.RiskCalculator import RiskCalculator


class BaseStrategy(ABC):
    trade_api: TradeAPI
    status_api: StatusAPI
    instrument: Instrument
    _strategy_order_dict: Dict[str, StrategyOrder]
    _strategy_measurement: StrategyMeasurement

    def __init__(self, api_key=API_KEY, api_key_secret=API_KEY_SECRET, api_passphrase=API_PASSPHRASE,
                 is_paper_trading: bool = IS_PAPER_TRADING):
        self.trade_api = TradeAPI(api_key=api_key, api_secret_key=api_key_secret, passphrase=api_passphrase,
                                  flag='0' if not is_paper_trading else '1', debug=False)
        self.status_api = StatusAPI(flag='0' if not is_paper_trading else '1', debug=False)
        self._strategy_order_dict = dict()
        self._strategy_measurement = StrategyMeasurement()
        self.params_loader = ParamsLoader()

    @abstractmethod
    def order_operation_decision(self) -> \
            Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]:
        pass

    def get_strategy_orders(self) -> Dict[str, StrategyOrder]:
        return self._strategy_order_dict.copy()

    def get_bid_strategy_orders(self) -> List[StrategyOrder]:
        """
        Fetch all buy strategy orders inside the BaseStrategy
        :return: List[StrategyOrder]
        """
        buy_orders = list()
        for cid, strategy_order in self._strategy_order_dict.items():
            if strategy_order.side == OrderSide.BUY:
                buy_orders.append(strategy_order)
        return sorted(buy_orders, key=lambda x: x.price, reverse=True)

    def get_ask_strategy_orders(self) -> List[StrategyOrder]:
        """
        Fetch all sell strategy orders inside the BaseStrategy
        :return: List[StrategyOrder]
        """
        sell_orders = list()
        for cid, strategy_order in self._strategy_order_dict.items():
            if strategy_order.side == OrderSide.SELL:
                sell_orders.append(strategy_order)
        return sorted(sell_orders, key=lambda x: x.price, reverse=False)

    def place_orders(self, order_request_list: List[PlaceOrderRequest]):
        """
        place order and cache strategy order, Maximum 20 orders can be placed per request
        :param order_request_list: https://www.okx.com/docs-v5/en/#rest-api-trade-place-multiple-orders
        :return:
        """
        order_data_list = []
        for order_request in order_request_list:
            strategy_order = StrategyOrder(
                inst_id=order_request.inst_id, ord_type=order_request.ord_type, side=order_request.side,
                size=order_request.size,
                price=order_request.price,
                client_order_id=order_request.client_order_id,
                strategy_order_status=StrategyOrderStatus.SENT, tgt_ccy=order_request.tgt_ccy
            )
            self._strategy_order_dict[order_request.client_order_id] = strategy_order
            order_data_list.append(order_request.to_dict())
            print(f"PLACE ORDER {order_request.ord_type.value} {order_request.side.value} {order_request.inst_id} "
                  f"{order_request.size} @ {order_request.price}")
            if len(order_data_list) >= 20:
                self._place_orders(order_data_list)
                order_data_list = []
        if order_data_list:
            self._place_orders(order_data_list)

    def _place_orders(self, order_data_list: List[Dict]):
        """
        Place order through REST API, check the individual order placing response,
        if successful, mark strategy orders as ACK
        if unsuccessful, delete the strategy orders from strategy order cache
        :param order_data_list: list of order requests' json
        :return: None
        """
        result = self.trade_api.place_multiple_orders(order_data_list)
        print(result)
        time.sleep(2)
        if result["code"] == '1':
            for order_data in order_data_list:
                client_order_id = order_data['clOrdId']
                if client_order_id in self._strategy_order_dict:
                    del self._strategy_order_dict[client_order_id]
        else:
            data = result['data']
            for single_order_data in data:
                client_order_id = single_order_data["clOrdId"]
                if client_order_id not in self._strategy_order_dict:
                    continue
                if single_order_data['sCode'] != '0':
                    del self._strategy_order_dict[client_order_id]
                    continue
                strategy_order: StrategyOrder = self._strategy_order_dict[client_order_id]
                strategy_order.order_id = single_order_data["ordId"]
                strategy_order.strategy_order_status = StrategyOrderStatus.ACK

    def amend_orders(self, order_request_list: List[AmendOrderRequest]):
        """
        amend order and cache strategy order,  Maximum 20 orders can be amended per request
        :param order_request_list: https://www.okx.com/docs-v5/en/#rest-api-trade-amend-multiple-orders
        :return:
        """
        order_data_list = []
        for order_request in order_request_list:
            client_order_id = order_request.client_order_id
            if client_order_id not in self._strategy_order_dict:
                continue
            strategy_order = self._strategy_order_dict[client_order_id]
            strategy_order.size = order_request.new_size
            strategy_order.price = order_request.new_price
            strategy_order.amend_req_id = order_request.req_id
            strategy_order.strategy_order_status = StrategyOrderStatus.AMD_SENT
            print(f"AMEND ORDER {order_request.client_order_id} with new size {order_request.new_size} or new price "
                  f"{order_request.new_price}, req_id is {order_request.req_id}")
            order_data_list.append(order_request.to_dict())
            if len(order_data_list) >= 20:
                self._amend_orders(order_data_list)
                order_data_list = []
        if order_data_list:
            self._amend_orders(order_data_list)

    def _amend_orders(self, order_data_list: List[Dict]):
        """
        Amend order through REST API, check the individual order amending response,
        Mark strategy orders as AMD_ACK, the strategy order status will be further confirmed by OMS update.
        :param order_data_list: list of order requests' json
        :return: None
        """
        result = self.trade_api.amend_multiple_orders(order_data_list)
        data = result['data']
        for single_order_data in data:
            client_order_id = single_order_data["clOrdId"]
            if client_order_id not in self._strategy_order_dict:
                continue
            if single_order_data['sCode'] != '0':
                continue
            strategy_order: StrategyOrder = self._strategy_order_dict[client_order_id]
            strategy_order.strategy_order_status = StrategyOrderStatus.AMD_ACK

    def cancel_orders(self, order_request_list: List[CancelOrderRequest]):
        """
        cancel order and cache strategy order, Maximum 20 orders can be canceled per request
        :param order_request_list: https://www.okx.com/docs-v5/en/#rest-api-trade-cancel-multiple-orders
        :return:
        """
        order_data_list = []
        for order_request in order_request_list:
            client_order_id = order_request.client_order_id
            if client_order_id not in self._strategy_order_dict:
                continue
            strategy_order = self._strategy_order_dict[client_order_id]
            strategy_order.strategy_order_status = StrategyOrderStatus.CXL_SENT
            print(f"CANCELING ORDER {order_request.client_order_id}")
            order_data_list.append(order_request.to_dict())
            if len(order_data_list) >= 20:
                self._cancel_orders(order_data_list)
                order_data_list = []
        if order_data_list:
            self._cancel_orders(order_data_list)

    def _cancel_orders(self, order_data_list: List[Dict]):
        """
        Cancel order through REST API, check the individual order canceling response,
        Mark strategy orders as CXL_ACK, the strategy order status will be further confirmed by OMS update.
        :param order_data_list: list of order requests' json
        :return: None
        """
        result = self.trade_api.cancel_multiple_orders(order_data_list)
        data = result['data']
        for single_order_data in data:
            client_order_id = single_order_data["clOrdId"]
            if client_order_id not in self._strategy_order_dict:
                continue
            if single_order_data['sCode'] != '0':
                continue
            strategy_order: StrategyOrder = self._strategy_order_dict[client_order_id]
            strategy_order.strategy_order_status = StrategyOrderStatus.CXL_ACK

    def cancel_all(self):
        """
        Canceling all existing strategy orders
        :return:
        """
        to_cancel = []
        for cid, strategy_order in self._strategy_order_dict.items():
            inst_id = strategy_order.inst_id
            cancel_req = CancelOrderRequest(inst_id=inst_id, client_order_id=cid)
            to_cancel.append(cancel_req)
        self.cancel_orders(to_cancel)

    @staticmethod
    def get_order_book() -> OrderBook:
        """
        Fetch order book object of the TRADING_INSTRUMENT_ID
        :return: OrderBook
        """
        if TRADING_INSTRUMENT_ID not in order_books:
            raise ValueError(f"{TRADING_INSTRUMENT_ID} not ready in order books cache!")
        order_book: OrderBook = order_books[TRADING_INSTRUMENT_ID]
        return order_book

    @staticmethod
    def get_account() -> Account:
        if not account_container:
            raise ValueError(f"account information not ready in accounts cache!")
        account: Account = account_container[0]
        return account

    @staticmethod
    def get_positions() -> Positions:
        if not positions_container:
            raise ValueError(f"positions information not ready in accounts cache!")
        positions: Positions = positions_container[0]
        return positions

    @staticmethod
    def get_tickers() -> Tickers:
        if not tickers_container:
            raise ValueError(f"tickers information not ready in accounts cache!")
        tickers: Tickers = tickers_container[0]
        return tickers

    @staticmethod
    def get_orders() -> Orders:
        if not orders_container:
            raise ValueError(f"order information not ready in orders cache!")
        orders: Orders = orders_container[0]
        return orders

    def _health_check(self) -> bool:
        try:
            order_book: OrderBook = self.get_order_book()
        except ValueError:
            return False
        order_book_delay = time.time() - order_book.timestamp / 1000
        if order_book_delay > ORDER_BOOK_DELAYED_SEC:
            logging.warning(f"{TRADING_INSTRUMENT_ID} delayed in order books cache for {order_book_delay:.2f} seconds!")
            return False
        try:
            account = self.get_account()
        except ValueError:
            return False
        account_delay = time.time() - account.u_time / 1000
        if account_delay > ACCOUNT_DELAYED_SEC:
            logging.warning(f"Account info delayed in accounts cache for {account_delay:.2f} seconds!")
            return False
        return True

    def _update_strategy_order_status(self):
        orders_cache: Orders = self.get_orders()
        order_not_found_in_cache = {}
        order_to_remove_from_cache = []
        for client_order_id in self._strategy_order_dict.copy():
            exchange_order: Order = orders_cache.get_order_by_client_order_id(client_order_id=client_order_id)
            strategy_order = self._strategy_order_dict[client_order_id]
            if not exchange_order:
                order_not_found_in_cache[client_order_id] = strategy_order
            if exchange_order.state == OrderState.LIVE:
                strategy_order.strategy_order_status = StrategyOrderStatus.LIVE
            filled_size_from_update = exchange_order.fill_sz - strategy_order.filled_size
            side_flag = 1 if exchange_order.side == OrderSide.BUY else -1
            self._strategy_measurement.net_filled_qty += filled_size_from_update * side_flag
            self._strategy_measurement.trading_volume += filled_size_from_update
            if side_flag == 1:
                self._strategy_measurement.buy_filled_qty += filled_size_from_update
            else:
                self._strategy_measurement.sell_filled_qty += filled_size_from_update
            if exchange_order.state == OrderState.CANCELED:
                del self._strategy_order_dict[client_order_id]
                order_to_remove_from_cache.append(exchange_order)
            if exchange_order.state == OrderState.PARTIALLY_FILLED:
                strategy_order.strategy_order_status = StrategyOrderStatus.PARTIALLY_FILLED
                strategy_order.filled_size = exchange_order.fill_sz
                strategy_order.avg_fill_price = exchange_order.fill_px
            if exchange_order.state == OrderState.FILLED:
                del self._strategy_order_dict[client_order_id]
                order_to_remove_from_cache.append(exchange_order)
        orders_cache.remove_orders(order_to_remove_from_cache)
        if order_not_found_in_cache:
            logging.warning(f"Strategy Orders not found in order cache: {order_not_found_in_cache}")

    def get_params(self):
        self.params_loader.load_params()

    def get_strategy_measurement(self):
        return self._strategy_measurement

    def risk_summary(self):
        print("===========  Strategy Summary  ==============")
        print(self._strategy_measurement)
        account = self.get_account()
        positions = self.get_positions()
        tickers = tickers_container[0]
        risk_snapshot = RiskCalculator.generate_risk_snapshot(account, positions, tickers)
        print(risk_snapshot)

    def check_status(self):
        status_response = self.status_api.status("ongoing")
        if status_response.get("data"):
            print(status_response.get("data"))
            return False
        return True

    def run(self):
        while 1:
            try:
                exchange_normal = self.check_status()
                if not exchange_normal:
                    raise ValueError("There is a ongoing maintenance in OKX.")
                self.get_params()
                result = self._health_check()
                if not result:
                    print(f"{result=}")
                    time.sleep(5)
                    continue
                # summary
                self.risk_summary()
                self._update_strategy_order_status()
                place_order_list, amend_order_list, cancel_order_list = self.order_operation_decision()
                # print(place_order_list)
                # print(amend_order_list)
                # print(cancel_order_list)

                self.place_orders(place_order_list)
                self.amend_orders(amend_order_list)
                self.cancel_orders(cancel_order_list)

                time.sleep(1)
            except:
                print(traceback.format_exc())
                try:
                    self.cancel_all()
                except:
                    print(f"Failed to cancel orders: {traceback.format_exc()}")
                time.sleep(20)

