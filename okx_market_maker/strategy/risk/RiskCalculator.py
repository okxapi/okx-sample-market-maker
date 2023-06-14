import time
from typing import Tuple

from okx_market_maker.settings import RISK_FREE_CCY_LIST
from okx_market_maker.strategy.risk.RiskSnapshot import RiskSnapShot
from okx_market_maker.position_management_service.model.Positions import Positions, Position
from okx_market_maker.position_management_service.model.Account import Account
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.utils.OkxEnum import InstType, CtType


class RiskCalculator:
    @classmethod
    def generate_risk_snapshot(cls, account: Account, positions: Positions, tickers: Tickers) -> RiskSnapShot:
        risk_snapshot = RiskSnapShot()
        account_detail = account.get_account_details()
        for ccy, detail in account_detail.items():
            usdt_price = tickers.get_usdt_price_by_ccy(ccy)
            cash = detail.cash_bal
            cash_usdt_value = cash * usdt_price
            risk_snapshot.asset_usdt_value += cash_usdt_value
            risk_snapshot.price_to_usdt_snapshot[ccy] = usdt_price
            risk_snapshot.asset_cash_snapshot[ccy] = cash
            if ccy not in RISK_FREE_CCY_LIST:
                risk_snapshot.delta_usdt_value += cash_usdt_value
        position_map = positions.get_position_map()
        for pos_id, position in position_map.items():
            inst_value_ccy, inst_value, inst_value_usdt = cls.calc_instrument_asset_value(position, tickers)
            inst_expo_ccy, inst_expo_value, inst_expo_value_usdt = cls.calc_instrument_delta(position, tickers)
            risk_snapshot.asset_usdt_value += inst_value_usdt
            risk_snapshot.asset_instrument_value_snapshot[
                f"{position.inst_id}|{position.pos_side.value}:{inst_value_ccy}"] = inst_value
            if inst_value_ccy not in risk_snapshot.price_to_usdt_snapshot:
                risk_snapshot.price_to_usdt_snapshot[inst_value_ccy] = tickers.get_usdt_price_by_ccy(inst_value_ccy)
            risk_snapshot.delta_usdt_value += inst_expo_value_usdt
            risk_snapshot.delta_instrument_snapshot[
                f"{position.inst_id}|{position.pos_side.value}:{inst_expo_ccy}"] = inst_expo_value
            if inst_expo_ccy not in risk_snapshot.price_to_usdt_snapshot:
                risk_snapshot.price_to_usdt_snapshot[inst_expo_ccy] = tickers.get_usdt_price_by_ccy(inst_expo_ccy)
        risk_snapshot.timestamp = int(time.time() * 1000)
        return risk_snapshot

    @classmethod
    def calc_instrument_asset_value(cls, position: Position, tickers: Tickers) -> Tuple[str, float, float]:
        inst_id = position.inst_id
        instrument = InstrumentUtil.get_instrument(inst_id)
        asset_value_ccy = InstrumentUtil.get_asset_value_ccy(instrument)
        price_to_usdt = tickers.get_usdt_price_by_ccy(asset_value_ccy)
        if instrument.inst_type == InstType.SWAP or instrument.inst_type == InstType.FUTURES:
            asset_value = position.upl
            return asset_value_ccy, asset_value, asset_value * price_to_usdt
        if instrument.inst_type == InstType.OPTION:
            asset_value = position.opt_val
            return asset_value_ccy, asset_value, asset_value * price_to_usdt
        return "USDT", 0, 0

    @classmethod
    def calc_instrument_delta(cls, position: Position, tickers: Tickers) -> Tuple[str, float, float]:
        inst_id = position.inst_id
        instrument = InstrumentUtil.get_instrument(inst_id)
        exposure_ccy = InstrumentUtil.get_asset_exposure_ccy(instrument)
        price_to_usdt = tickers.get_usdt_price_by_ccy(exposure_ccy)
        if instrument.inst_type == InstType.SWAP or instrument.inst_type == InstType.FUTURES:
            if instrument.ct_type == CtType.LINEAR:
                ccy_exposure = position.pos * instrument.ct_mul * instrument.ct_val
                return exposure_ccy, ccy_exposure, ccy_exposure * price_to_usdt
            if instrument.ct_type == CtType.INVERSE:
                ccy_exposure = position.pos * instrument.ct_mul * instrument.ct_val / position.avg_px
                return exposure_ccy, ccy_exposure, ccy_exposure * price_to_usdt
        if instrument.inst_type == InstType.OPTION:
            ccy_exposure = position.delta_bs
            return exposure_ccy, ccy_exposure, ccy_exposure * price_to_usdt
        return "USDT", 0, 0

