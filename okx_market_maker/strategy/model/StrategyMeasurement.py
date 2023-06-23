import datetime
from dataclasses import dataclass
from decimal import Decimal

from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.strategy.risk.RiskSnapshot import RiskSnapShot
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.settings import TRADING_INSTRUMENT_ID
from okx_market_maker.utils.OkxEnum import InstType
from okx_market_maker import tickers_container

@dataclass
class StrategyMeasurement:
    net_filled_qty: Decimal = 0
    buy_filled_qty: Decimal = 0
    sell_filled_qty: Decimal = 0
    trading_volume: Decimal = 0

    asset_value_change_in_usdt_since_running: float = 0
    pnl_in_usdt_since_running: float = 0
    trading_instrument_exposure_in_base: float = 0
    trading_instrument_exposure_in_usdt: float = 0
    trading_inst_exposure_ccy: str = ""
    _current_risk_snapshot: RiskSnapShot = None
    _inception_risk_snapshot: RiskSnapShot = None

    def calc_pnl(self):
        pnl = 0
        delta_map = {}
        for ccy in self._current_risk_snapshot.asset_cash_snapshot:
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] += self._current_risk_snapshot.asset_cash_snapshot[ccy]
        for key in self._current_risk_snapshot.asset_instrument_value_snapshot:
            ccy = key.split(":")[-1]
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] += self._current_risk_snapshot.asset_instrument_value_snapshot[key]
        for ccy in self._inception_risk_snapshot.asset_cash_snapshot:
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] -= self._inception_risk_snapshot.asset_cash_snapshot[ccy]
        for key in self._inception_risk_snapshot.asset_instrument_value_snapshot:
            ccy = key.split(":")[-1]
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] -= self._inception_risk_snapshot.asset_instrument_value_snapshot[key]
        for ccy in delta_map:
            price = self._current_risk_snapshot.price_to_usdt_snapshot.get(ccy)
            if not price:
                tickers: Tickers = tickers_container[0]
                price = tickers.get_usdt_price_by_ccy(ccy)
            pnl += price * delta_map[ccy]
        return pnl

    def consume_risk_snapshot(self, risk_snapshot: RiskSnapShot):
        if self._inception_risk_snapshot is None:
            self._inception_risk_snapshot = risk_snapshot
            return
        self._current_risk_snapshot = risk_snapshot
        self.asset_value_change_in_usdt_since_running = \
            self._current_risk_snapshot.asset_usdt_value - self._inception_risk_snapshot.asset_usdt_value
        self.pnl_in_usdt_since_running = self.calc_pnl()
        instrument = InstrumentUtil.get_instrument(TRADING_INSTRUMENT_ID)
        exposure_ccy = InstrumentUtil.get_asset_exposure_ccy(instrument)
        self.trading_inst_exposure_ccy = exposure_ccy
        price = self._current_risk_snapshot.price_to_usdt_snapshot.get(exposure_ccy)
        if instrument.inst_type == InstType.SPOT:
            current_cash = self._current_risk_snapshot.asset_cash_snapshot.get(exposure_ccy)
            init_cash = self._inception_risk_snapshot.asset_cash_snapshot.get(exposure_ccy)
            self.trading_instrument_exposure_in_base = current_cash - init_cash
            self.trading_instrument_exposure_in_usdt = (current_cash - init_cash) * price
        if instrument.inst_type in [InstType.SWAP, InstType.FUTURES, InstType.OPTION]:
            delta = 0
            for key, value in self._current_risk_snapshot.delta_instrument_snapshot.items():
                if TRADING_INSTRUMENT_ID in key:
                    delta += value
            init_delta = 0
            for key, value in self._inception_risk_snapshot.delta_instrument_snapshot.items():
                if TRADING_INSTRUMENT_ID in key:
                    init_delta += value
            self.trading_instrument_exposure_in_base = delta - init_delta
            self.trading_instrument_exposure_in_usdt = (delta - init_delta) * price
        self.print_risk_summary()

    def print_risk_summary(self):
        print(f"==== Risk Summary ====\n"
              f"Time: "
              f"{datetime.datetime.fromtimestamp(self._current_risk_snapshot.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
              f"Inception: "
              f"{datetime.datetime.fromtimestamp(self._inception_risk_snapshot.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n"
              f"Asset Value Change since inception(USDT): {self.asset_value_change_in_usdt_since_running:.2f}\n"
              f"P&L since inception(USDT): {self.pnl_in_usdt_since_running:.2f}\n"
              f"Trading Instrument: {TRADING_INSTRUMENT_ID}\n"
              f"Trading Instrument Exposure ({self.trading_inst_exposure_ccy}): "
              f"{self.trading_instrument_exposure_in_base:.4f}\nTrading Instrument Exposure (USDT): "
              f"{self.trading_instrument_exposure_in_usdt:.2f}\nNet Traded Position: {self.net_filled_qty}\n"
              f"Net Trading Volume: {self.trading_volume}\n==== End of Summary ====")
