from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch, MagicMock

from okx_market_maker.market_data_service.model.OrderBook import OrderBookLevel
from okx_market_maker.order_management_service.model.Order import Orders, Order
from okx_market_maker.position_management_service.model.Account import Account
from okx_market_maker.settings import ORDER_BOOK_DELAYED_SEC, ACCOUNT_DELAYED_SEC
from okx_market_maker.strategy.SampleMM import SampleMM, OrderBook, TRADING_INSTRUMENT_ID
from okx_market_maker.strategy.model.StrategyOrder import StrategyOrder, StrategyOrderStatus
from okx_market_maker.utils.OkxEnum import OrderState, OrderSide, OrderType, AccountConfigMode, InstType, TdMode
from okx_market_maker.utils.TdModeUtil import TdModeUtil


class TestStrategy(TestCase):
    def setUp(self) -> None:
        strategy = SampleMM()
        self.strategy = strategy
        self.strategy.set_strategy_measurement("BTC-USDT-SWAP", trading_instrument_type=InstType.SWAP)
        order_book = OrderBook(TRADING_INSTRUMENT_ID)
        order_book.set_asks_on_update(OrderBookLevel(price=2, quantity=2, order_count=1, price_string="2",
                                                     quantity_string="2", order_count_string="1"))
        order_book.set_bids_on_update(OrderBookLevel(price=1, quantity=1, order_count=1, price_string="1",
                                                     quantity_string="1", order_count_string="1"))
        order_book.set_timestamp(1234000)
        self.order_book = order_book
        account = Account()
        account.u_time = 1234
        self.account = account
        self.strategy.get_order_book = MagicMock(return_value=order_book)
        self.strategy.get_account = MagicMock(return_value=account)
        self.strategy.mds.stop_service = MagicMock(return_value=None)
        self.strategy.mds.run_service = MagicMock(return_value=None)

    def test_check_status(self):
        self.strategy.status_api.status = MagicMock(return_value={
            "code": "0",
            "data": [
                {
                    "begin": "1672823400000",
                    "end": "1672823520000",
                    "href": "",
                    "preOpenBegin": "",
                    "scheDesc": "",
                    "serviceType": "8",
                    "state": "ongoing",
                    "maintType": "1",
                    "env": "1",
                    "system": "unified",
                    "title": "Trading account system upgrade (in batches of accounts)"
                }
            ],
            "msg": ""
        })
        self.assertFalse(self.strategy.check_status())
        self.strategy.status_api.status = MagicMock(return_value={
            "code": "0",
            "data": [],
            "msg": ""
        })
        self.assertTrue(self.strategy.check_status())

    @patch("time.time", return_value=1234+ORDER_BOOK_DELAYED_SEC+1)
    def test_health_check_orderbook_timeout(self, time_mock):
        self.assertFalse(self.strategy._health_check())

    @patch("time.time", return_value=1235)
    def test_health_check_checksum_failed(self, time_mock):
        self.order_book.do_check_sum = MagicMock(return_value=False)
        self.assertFalse(self.strategy._health_check())
        self.strategy.mds.stop_service.assert_called_once()
        self.strategy.mds.run_service.assert_called_once()

    @patch("time.time", return_value=1234 + ACCOUNT_DELAYED_SEC + 1)
    def test_health_check_account_timeout(self, time_mock):
        self.order_book.timestamp = 1234 + ACCOUNT_DELAYED_SEC
        self.assertFalse(self.strategy._health_check())

    def test_update_strategy_order(self):
        order1 = Order(cl_ord_id="order1", ord_id='1', state=OrderState.LIVE, side=OrderSide.BUY)
        order2 = Order(cl_ord_id="order2", ord_id='2', state=OrderState.CANCELED, side=OrderSide.BUY)
        order3 = Order(cl_ord_id="order3", ord_id='3', state=OrderState.FILLED, acc_fill_sz="1", side=OrderSide.BUY)
        order4 = Order(cl_ord_id="order4", ord_id='4', state=OrderState.PARTIALLY_FILLED, acc_fill_sz="0.5",
                       side=OrderSide.BUY)
        orders = Orders(
            _order_map={'1': order1, "2": order2, "3": order3, "4": order4},
            _client_order_map={"order1": order1, "order2": order2, "order3": order3, "order4": order4,}
        )
        self.strategy.get_orders = MagicMock(side_effect=lambda: orders)
        self.strategy._strategy_order_dict = {
            "order1": StrategyOrder(inst_id=TRADING_INSTRUMENT_ID, side=OrderSide.BUY, ord_type=OrderType.LIMIT,
                                    size="1", price="1", strategy_order_status=StrategyOrderStatus.SENT),
            "order2": StrategyOrder(inst_id=TRADING_INSTRUMENT_ID, side=OrderSide.BUY, ord_type=OrderType.LIMIT,
                                    size="1", price="1", strategy_order_status=StrategyOrderStatus.LIVE),
            "order3": StrategyOrder(inst_id=TRADING_INSTRUMENT_ID, side=OrderSide.BUY, ord_type=OrderType.LIMIT,
                                    size="1", price="1", strategy_order_status=StrategyOrderStatus.LIVE),
            "order4": StrategyOrder(inst_id=TRADING_INSTRUMENT_ID, side=OrderSide.BUY, ord_type=OrderType.LIMIT,
                                    size="1", price="1", strategy_order_status=StrategyOrderStatus.LIVE),
        }
        self.strategy._update_strategy_order_status()
        self.assertIn("order1", self.strategy._strategy_order_dict)
        self.assertEqual(self.strategy._strategy_order_dict["order1"].strategy_order_status, StrategyOrderStatus.LIVE)
        self.assertNotIn("order2", self.strategy._strategy_order_dict)
        self.assertNotIn("order3", self.strategy._strategy_order_dict)
        self.assertIn("order4", self.strategy._strategy_order_dict)
        self.assertEqual(self.strategy._strategy_order_dict["order4"].strategy_order_status,
                         StrategyOrderStatus.PARTIALLY_FILLED)
        self.assertEqual(self.strategy._strategy_order_dict["order4"].filled_size, order4.acc_fill_sz)
        self.assertEqual(self.strategy._strategy_measurement.net_filled_qty, Decimal("1.5"))

    def test_decide_td_mode(self):
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.CASH, InstType.SPOT, td_mode_setting="cross")
        self.assertEqual(td_mode, TdMode.CASH)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.CASH, InstType.OPTION, td_mode_setting="cross")
        self.assertEqual(td_mode, TdMode.CASH)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.SINGLE_CCY_MARGIN, InstType.SPOT,
                                                 td_mode_setting="cross")
        self.assertEqual(td_mode, TdMode.CASH)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.SINGLE_CCY_MARGIN, InstType.OPTION,
                                                 td_mode_setting="cross")
        self.assertEqual(td_mode, TdMode.CROSS)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.SINGLE_CCY_MARGIN, InstType.SWAP,
                                                 td_mode_setting="isolated")
        self.assertEqual(td_mode, TdMode.ISOLATED)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.MULTI_CCY_MARGIN, InstType.SPOT,
                                                 td_mode_setting="isolated")
        self.assertEqual(td_mode, TdMode.CROSS)
        td_mode = TdModeUtil.decide_trading_mode(AccountConfigMode.MULTI_CCY_MARGIN, InstType.MARGIN,
                                                 td_mode_setting="cross")
        self.assertEqual(td_mode, TdMode.ISOLATED)
