import time
from typing import Tuple

from okx_market_maker.settings import RISK_FREE_CCY_LIST
from okx_market_maker.strategy.risk.RiskSnapshot import RiskSnapShot, AssetValueInst
from okx_market_maker.position_management_service.model.Positions import Positions, Position
from okx_market_maker.position_management_service.model.Account import Account
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.market_data_service.model.MarkPx import MarkPxCache
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.utils.OkxEnum import InstType, CtType


class RiskCalculator:
    @classmethod
    def generate_risk_snapshot(cls, account: Account, positions: Positions, tickers: Tickers,
                               mark_px_cache: MarkPxCache) -> RiskSnapShot:
        risk_snapshot = RiskSnapShot()
        risk_snapshot.asset_usd_value = account.total_eq
        usdt_to_usd_rate = mark_px_cache.get_usdt_to_usd_rate()
        account_detail = account.get_account_details()
        for ccy, detail in account_detail.items():
            usdt_price = tickers.get_usdt_price_by_ccy(ccy)
            usd_price = usdt_price * usdt_to_usd_rate
            cash = detail.cash_bal
            cash_usd_value = cash * usd_price
            risk_snapshot.price_to_usd_snapshot[ccy] = usd_price
            risk_snapshot.asset_cash_snapshot[ccy] = cash
            if ccy not in RISK_FREE_CCY_LIST:
                risk_snapshot.delta_usd_value += cash_usd_value
        position_map = positions.get_position_map()
        for pos_id, position in position_map.items():
            inst_value_ccy, inst_value = cls.calc_instrument_asset_value(position)
            inst_expo_ccy, inst_expo_value = cls.calc_instrument_delta(position)
            risk_snapshot.asset_instrument_value_snapshot[
                f"{position.inst_id}|{position.mgn_mode.value}|{position.pos_side.value}:{inst_value_ccy}"] = inst_value
            risk_snapshot.mark_px_instrument_snapshot[inst_value.instrument.inst_id] = inst_value.mark_px
            if inst_value_ccy not in risk_snapshot.price_to_usd_snapshot:
                risk_snapshot.price_to_usd_snapshot[inst_value_ccy] = tickers.get_usdt_price_by_ccy(inst_value_ccy)
            if inst_expo_ccy not in risk_snapshot.price_to_usd_snapshot:
                usd_price = tickers.get_usdt_price_by_ccy(inst_expo_ccy) * usdt_to_usd_rate
                risk_snapshot.price_to_usd_snapshot[inst_expo_ccy] = usd_price
            else:
                usd_price = risk_snapshot.price_to_usd_snapshot[inst_expo_ccy]
            risk_snapshot.delta_usd_value += inst_expo_value * usd_price
            risk_snapshot.delta_instrument_snapshot[
                f"{position.inst_id}|{position.mgn_mode.value}|{position.pos_side.value}:{inst_expo_ccy}"] = \
                inst_expo_value
            quote_ccy = position.inst_id.split("-")[1]
            if quote_ccy not in risk_snapshot.price_to_usd_snapshot:
                usd_price = tickers.get_usdt_price_by_ccy(quote_ccy) * usdt_to_usd_rate
                risk_snapshot.price_to_usd_snapshot[inst_expo_ccy] = usd_price
        risk_snapshot.timestamp = int(time.time() * 1000)
        return risk_snapshot

    @classmethod
    def calc_instrument_asset_value(cls, position: Position) -> Tuple[str, AssetValueInst]:
        inst_id = position.inst_id
        guessed_inst_type = InstrumentUtil.get_inst_type_from_inst_id(inst_id)
        if guessed_inst_type == InstType.SPOT:
            instrument = InstrumentUtil.get_instrument(inst_id, query_inst_type=InstType.MARGIN)
        else:
            instrument = InstrumentUtil.get_instrument(inst_id)
        asset_value_ccy = InstrumentUtil.get_asset_value_ccy(instrument, position)
        if instrument.inst_type == InstType.MARGIN:
            asset_value = position.upl + position.margin
            asset_value_inst = AssetValueInst(instrument=instrument, asset_value=asset_value, margin=position.margin,
                                              pos=position.pos, mark_px=position.mark_px, avg_px=position.avg_px,
                                              liability=position.liability, pos_ccy=position.pos_ccy, ccy=position.ccy)
            return asset_value_ccy, asset_value_inst
        if instrument.inst_type == InstType.SWAP or instrument.inst_type == InstType.FUTURES:
            asset_value = position.upl + position.margin
            asset_value_inst = AssetValueInst(instrument=instrument, asset_value=asset_value, margin=position.margin,
                                              pos=position.pos, mark_px=position.mark_px, avg_px=position.avg_px)
            return asset_value_ccy, asset_value_inst
        if instrument.inst_type == InstType.OPTION:
            asset_value = position.opt_val + position.margin
            asset_value_inst = AssetValueInst(instrument=instrument, asset_value=asset_value, margin=position.margin,
                                              pos=position.pos, mark_px=position.mark_px)
            return asset_value_ccy, asset_value_inst

    @classmethod
    def calc_instrument_delta(cls, position: Position) -> Tuple[str, float]:
        inst_id = position.inst_id
        guessed_inst_type = InstrumentUtil.get_inst_type_from_inst_id(inst_id)
        if guessed_inst_type == InstType.SPOT:
            instrument = InstrumentUtil.get_instrument(inst_id, query_inst_type=InstType.MARGIN)
        else:
            instrument = InstrumentUtil.get_instrument(inst_id)
        exposure_ccy = InstrumentUtil.get_asset_exposure_ccy(instrument)
        if instrument.inst_type == InstType.MARGIN:
            ccy_exposure = position.pos
            return exposure_ccy, ccy_exposure
        if instrument.inst_type == InstType.SWAP or instrument.inst_type == InstType.FUTURES:
            if instrument.ct_type == CtType.LINEAR:
                ccy_exposure = position.pos * instrument.ct_mul * instrument.ct_val
                return exposure_ccy, ccy_exposure
            if instrument.ct_type == CtType.INVERSE:
                ccy_exposure = position.pos * instrument.ct_mul * instrument.ct_val / position.avg_px
                return exposure_ccy, ccy_exposure
        if instrument.inst_type == InstType.OPTION:
            ccy_exposure = position.delta_bs
            return exposure_ccy, ccy_exposure
        return "USDT", 0

