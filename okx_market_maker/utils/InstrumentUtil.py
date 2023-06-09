import math

from okx.PublicData import PublicAPI

from okx_market_maker import instruments
from okx_market_maker.settings import IS_PAPER_TRADING
from okx_market_maker.utils.OkxEnum import InstType, OrderSide, InstState
from okx_market_maker.market_data_service.model.Instrument import Instrument


class InstrumentUtil:
    public_api = PublicAPI(flag='0' if not IS_PAPER_TRADING else '1')

    @classmethod
    def get_inst_type_from_inst_id(cls, inst_id: str) -> InstType:
        inst_id_parts = inst_id.split("-")
        if len(inst_id_parts) < 2 or len(inst_id_parts) > 5 or len(inst_id_parts) == 4:
            raise ValueError(f"Invalid InstId {inst_id}")
        if len(inst_id_parts) == 2:
            return InstType.SPOT
        if len(inst_id_parts) == 3:
            if inst_id_parts[2] == "SWAP":
                return InstType.SWAP
            else:
                return InstType.FUTURES
        if len(inst_id_parts) == 5:
            return InstType.OPTION

    @classmethod
    def get_instrument(cls, inst_id: str) -> Instrument:
        if inst_id in instruments:
            return instruments[inst_id]
        inst_type = InstrumentUtil.get_inst_type_from_inst_id(inst_id)
        uly = ''
        if inst_type == InstType.OPTION:
            uly = inst_id.split('-')[0] + '-' + inst_id.split('-')[1]
        inst_result = cls.public_api.get_instruments(instType=inst_type.value, instId=inst_id, uly=uly)
        if inst_result.get("code") != '0':
            raise ValueError(f"{inst_id} inst not exists in OKX: {inst_result}")
        data = inst_result["data"]
        json_response = data[0]
        instrument = Instrument.init_from_json(json_response)
        if instrument.state != InstState.LIVE:
            raise ValueError(f"{inst_id} inst state error in OKX: {instrument.state}")
        instruments[instrument.inst_id] = instrument
        return instrument

    @classmethod
    def price_trim_by_tick_sz(cls, price: float, side: OrderSide, instrument: Instrument) -> float:
        if side == OrderSide.BUY:
            return math.floor(price / instrument.tick_sz) * instrument.tick_sz
        else:
            return math.ceil(price / instrument.tick_sz) * instrument.tick_sz

    @classmethod
    def quantity_trim_by_lot_sz(cls, quantity: float, instrument: Instrument) -> float:
        return round(quantity / instrument.lot_sz) * instrument.lot_sz

    @classmethod
    def get_asset_value_ccy(cls, instrument: Instrument) -> str:
        return instrument.settle_ccy

    @classmethod
    def get_asset_exposure_ccy(cls, instrument: Instrument) -> str:
        return instrument.inst_id.split("-")[0]
