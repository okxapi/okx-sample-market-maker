import math
import time
from decimal import Decimal
from typing import Tuple, List

from okx_market_maker.market_data_service.model.Instrument import Instrument
from okx_market_maker.market_data_service.model.OrderBook import OrderBook
from okx_market_maker.order_management_service.model.OrderRequest import PlaceOrderRequest, AmendOrderRequest, \
    CancelOrderRequest
from okx_market_maker.strategy.BaseStrategy import BaseStrategy, StrategyOrder, TRADING_INSTRUMENT_ID
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.utils.OkxEnum import TdMode, OrderSide, OrderType, PosSide, InstType
from okx_market_maker.utils.WsOrderUtil import get_request_uuid


class SampleMM(BaseStrategy):
    def __init__(self):
        super().__init__()

    def order_operation_decision(self) -> \
            Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]:
        """
        Custom Market Making Logic -> propose a group of market making orders
        :return:
        """
        order_book: OrderBook = self.get_order_book()
        bid_level = order_book.bid_by_level(1)
        ask_level = order_book.ask_by_level(1)
        if not bid_level and not ask_level:
            raise ValueError("Empty order book!")
        if bid_level and not ask_level:
            ask_level = order_book.bid_by_level(1)
        if ask_level and not bid_level:
            bid_level = order_book.ask_by_level(1)
        instrument = InstrumentUtil.get_instrument(TRADING_INSTRUMENT_ID, self.trading_instrument_type)
        step_pct = self.params_loader.get_strategy_params("step_pct")
        num_of_order_each_side = self.params_loader.get_strategy_params("num_of_order_each_side")
        single_order_size = max(
            self.params_loader.get_strategy_params("single_size_as_multiple_of_lot_size") * instrument.lot_sz,
            instrument.min_sz)
        strategy_measurement = self.get_strategy_measurement()
        buy_num_of_order_each_side = num_of_order_each_side
        sell_num_of_order_each_side = num_of_order_each_side
        max_net_buy = self.params_loader.get_strategy_params("maximum_net_buy")
        max_net_sell = self.params_loader.get_strategy_params("maximum_net_sell")
        if strategy_measurement.net_filled_qty > 0:
            buy_num_of_order_each_side *= max(1 - strategy_measurement.net_filled_qty / max_net_buy, 0)
            buy_num_of_order_each_side = math.ceil(buy_num_of_order_each_side)
        if strategy_measurement.net_filled_qty < 0:
            sell_num_of_order_each_side *= max(1 + strategy_measurement.net_filled_qty / max_net_sell, 0)
            sell_num_of_order_each_side = math.ceil(sell_num_of_order_each_side)
        proposed_buy_orders = [(bid_level.price * (1 - step_pct * (i + 1)), single_order_size)
                               for i in range(buy_num_of_order_each_side)]
        proposed_sell_orders = [(ask_level.price * (1 + step_pct * (i + 1)), single_order_size)
                                for i in range(sell_num_of_order_each_side)]

        proposed_buy_orders = [(InstrumentUtil.price_trim_by_tick_sz(price_qty[0], OrderSide.BUY, instrument),
                                InstrumentUtil.quantity_trim_by_lot_sz(price_qty[1], instrument))
                               for price_qty in proposed_buy_orders]
        proposed_sell_orders = [(InstrumentUtil.price_trim_by_tick_sz(price_qty[0], OrderSide.SELL, instrument),
                                 InstrumentUtil.quantity_trim_by_lot_sz(price_qty[1], instrument))
                                for price_qty in proposed_sell_orders]
        current_buy_orders = self.get_bid_strategy_orders()
        current_sell_orders = self.get_ask_strategy_orders()

        buy_to_place, buy_to_amend, buy_to_cancel = self.get_req(
            proposed_buy_orders, current_buy_orders, OrderSide.BUY, instrument)
        sell_to_place, sell_to_amend, sell_to_cancel = self.get_req(
            proposed_sell_orders, current_sell_orders, OrderSide.SELL, instrument)
        return buy_to_place + sell_to_place, buy_to_amend + sell_to_amend, buy_to_cancel + sell_to_cancel

    def get_req(self, propose_orders: List[Tuple[str, str]],
                current_orders: List[StrategyOrder], side: OrderSide, instrument: Instrument) -> \
            Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]:
        """
        Compare proposed orders(PO) with current orders(CO), all with the same OrderSide (buy or sell orders)
        1. if the price-size pair from PO exists in CO, keep the order intact.
        2. if more PO than CO, PLACE new orders in PO' tail. i.e. if PO has (a, b, c), CO has (a1, b1),
        place a new order for order c.
        3. if more CO than PO, CANCEL existing orders in CO' tail. i.e. if PO has (a, b), CO has (a1, b1, c1),
        cancel order c1.
        4. For other PO, AMEND existing CO with new price or new size or both.
        :return: Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]
        """
        to_place: List[PlaceOrderRequest] = []
        to_amend: List[AmendOrderRequest] = []
        to_cancel: List[CancelOrderRequest] = []
        for strategy_order in current_orders.copy():
            price = strategy_order.price
            remaining_size = float(strategy_order.size) - float(strategy_order.filled_size)
            remaining_size = InstrumentUtil.quantity_trim_by_lot_sz(remaining_size, instrument)
            if (price, remaining_size) in propose_orders:
                current_orders.remove(strategy_order)
                propose_orders.remove((price, remaining_size))
        for i in range(max(len(propose_orders), len(current_orders))):
            if i + 1 > len(current_orders):
                price, size = propose_orders[i]
                order_req = PlaceOrderRequest(
                    inst_id=instrument.inst_id, td_mode=self.decide_td_mode(instrument), side=side,
                    ord_type=OrderType.LIMIT,
                    size=size,
                    price=price,
                    client_order_id=get_request_uuid("order"),
                    pos_side=PosSide.net,
                    ccy=(instrument.base_ccy if side == OrderSide.BUY else instrument.quote_ccy)
                    if instrument.inst_type == InstType.MARGIN else ""
                )
                to_place.append(order_req)
                continue  # to new
            if i + 1 > len(propose_orders):
                strategy_order = current_orders[i]
                cid = strategy_order.client_order_id
                inst_id = strategy_order.inst_id
                cancel_req = CancelOrderRequest(inst_id=inst_id, client_order_id=cid)
                to_cancel.append(cancel_req)
                continue  # to cancel current
            # to amend
            strategy_order = current_orders[i]
            new_price, new_size = propose_orders[i]
            remaining_size = (Decimal(strategy_order.size) - Decimal(strategy_order.filled_size)).to_eng_string()
            cid = strategy_order.client_order_id
            amend_req = AmendOrderRequest(strategy_order.inst_id, client_order_id=cid,
                                          req_id=get_request_uuid("amend"))
            if new_price != strategy_order.price:
                amend_req.new_price = new_price
            if new_size != remaining_size:
                amend_req.new_size = (Decimal(strategy_order.filled_size) + Decimal(new_size)).to_eng_string()
            to_amend.append(amend_req)
        return to_place, to_amend, to_cancel
