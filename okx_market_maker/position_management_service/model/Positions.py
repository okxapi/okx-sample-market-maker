from dataclasses import dataclass, field
from okx_market_maker.utils.OkxEnum import *
from typing import Dict


@dataclass
class Position:
    inst_type: InstType = None
    mgn_mode: MgnMode = None
    position_id: str = ""
    trade_id: str = ""
    inst_id: str = ""
    pos_side: PosSide = None
    pos: float = 0

    base_bal: float = 0
    quote_bal: float = 0
    base_borrowed: float = 0
    base_interest: float = 0
    quote_borrowed: float = 0
    quote_interest: float = 0

    ccy: str = ""
    pos_ccy: str = ""
    avail_pos: float = 0
    avg_px: float = 0
    upl: float = 0
    upl_ratio: float = 0
    upl_last_px: float = 0
    upl_ratio_last_px: float = 0
    lever: int = 0

    last: float = 0
    liq_px: float = 0
    mark_px: float = 0
    usd_px: float = 0
    imr: float = 0
    margin: float = 0
    mgn_ratio: float = 0
    mmr: float = 0
    liability: float = 0
    liability_ccy: str = ""
    interest: float = 0

    notional_usd: float = 0
    opt_val: float = 0
    adl: int = 0
    biz_ref_type: str = ""

    delta_bs: float = 0
    delta_pa: float = 0
    gamma_bs: float = 0
    gamma_pa: float = 0
    theta_bs: float = 0
    theta_pa: float = 0
    vega_bs: float = 0
    vega_pa: float = 0

    spot_in_use_amt: float = 0
    spot_in_use_ccy: str = ""

    u_time: int = 0
    p_time: int = 0
    ctime: int = 0

    @classmethod
    def init_from_json(cls, json_response):
        position = Position()
        position.inst_type = InstType[json_response["instType"]]
        position.mgn_mode = MgnMode[json_response["mgnMode"]]
        position.position_id = str(json_response["posId"])
        position.ccy = json_response["ccy"]
        position.trade_id = json_response.get("tradeId", "")
        position.inst_id = json_response.get("instId", "")
        position.pos_side = PosSide[json_response["posSide"]]
        position.pos = float(json_response.get("pos", 0))
        position.base_bal = float(json_response.get("baseBal")) if json_response.get("baseBal") else 0
        position.quote_bal = float(json_response.get("quoteBal")) if json_response.get("quoteBal") else 0
        position.base_borrowed = float(json_response.get("baseBorrowed")) if json_response.get("baseBorrowed") else 0
        position.base_interest = float(json_response.get("baseInterest")) if json_response.get("baseInterest") else 0
        position.quote_borrowed = float(json_response.get("quoteBorrowed")) if json_response.get("quoteBorrowed") else 0
        position.quote_interest = float(json_response.get("quoteInterest")) if json_response.get("quoteInterest") else 0

        position.pos_ccy = json_response["posCcy"]
        position.avail_pos = float(json_response.get("availPos")) if json_response.get("availPos") else 0
        position.avg_px = float(json_response.get("avgPx")) if json_response.get("avgPx") else 0
        position.upl = float(json_response.get("upl")) if json_response.get("upl") else 0
        position.upl_ratio = float(json_response.get("uplRatio")) if json_response.get("uplRatio") else 0
        position.upl_last_px = float(json_response.get("uplLastPx")) if json_response.get("uplLastPx") else 0
        position.upl_ratio_last_px = float(json_response.get("uplRatioLastPx")) \
            if json_response.get("uplRatioLastPx") else 0
        position.lever = float(json_response.get("lever")) if json_response.get("lever") else 0

        position.last = float(json_response.get("last")) if json_response.get("last") else 0
        position.liq_px = float(json_response.get("liqPx")) if json_response.get("liqPx") else 0
        position.mark_px = float(json_response.get("markPx")) if json_response.get("markPx") else 0
        position.usd_px = float(json_response.get("usdPx")) if json_response.get("usdPx") else 0
        position.imr = float(json_response.get("imr")) if json_response.get("imr") else 0
        position.margin = float(json_response.get("margin")) if json_response.get("margin") else 0
        position.mgn_ratio = float(json_response.get("mgnRatio")) if json_response.get("mgnRatio") else 0
        position.mmr = float(json_response.get("mmr")) if json_response.get("mmr") else 0
        position.liability = float(json_response.get("liab")) if json_response.get("liab") else 0
        position.liability_ccy = json_response["liabCcy"]
        position.interest = float(json_response.get("interest")) if json_response.get("interest") else 0

        position.notional_usd = float(json_response.get("notionalUsd")) if json_response.get("notionalUsd") else 0
        position.opt_val = float(json_response.get("optVal")) if json_response.get("optVal") else 0
        position.adl = int(json_response.get("adl")) if json_response.get("adl") else 0
        position.biz_ref_type = json_response.get("bizRefType", "")

        position.delta_bs = float(json_response.get("deltaBS")) if json_response.get("deltaBS") else 0
        position.delta_pa = float(json_response.get("deltaPA")) if json_response.get("deltaPA") else 0
        position.gamma_bs = float(json_response.get("gammaBS")) if json_response.get("gammaBS") else 0
        position.gamma_pa = float(json_response.get("gammaPA")) if json_response.get("gammaPA") else 0
        position.theta_bs = float(json_response.get("thetaBS")) if json_response.get("thetaBS") else 0
        position.theta_pa = float(json_response.get("thetaPA")) if json_response.get("thetaPA") else 0
        position.vega_bs = float(json_response.get("vegaBS")) if json_response.get("vegaBS") else 0
        position.vega_pa = float(json_response.get("vegaPA")) if json_response.get("vegaPA") else 0

        position.spot_in_use_amt = float(json_response.get("spotInUseAmt")) if json_response.get("spotInUseAmt") else 0
        position.spot_in_use_ccy = json_response.get("spotInUseCcy", "")

        position.u_time = int(json_response.get("uTime", 0))
        position.p_time = int(json_response.get("pTime", 0))
        position.ctime = int(json_response.get("cTime", 0))
        return position


@dataclass
class Positions:
    _position_map: Dict[str, Position] = field(default_factory=lambda: dict())

    @classmethod
    def init_from_json(cls, json_response):
        data = json_response["data"]
        positions = Positions()
        positions._position_map = {single_pos["posId"]: Position.init_from_json(single_pos)
                                   for single_pos in data}
        return positions

    def update_from_json(self, json_response):
        data = json_response["data"]
        for single_pos in data:
            new_pos = Position.init_from_json(single_pos)
            if new_pos.pos == 0 and new_pos.position_id in self._position_map:
                del self._position_map[new_pos.position_id]
                continue
            self._position_map[new_pos.position_id] = new_pos

    def get_position_map(self) -> Dict[str, Position]:
        return self._position_map
