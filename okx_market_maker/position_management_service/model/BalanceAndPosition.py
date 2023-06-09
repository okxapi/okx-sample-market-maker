from dataclasses import dataclass, field
from okx_market_maker.utils.OkxEnum import *
from typing import Dict


@dataclass
class BalanceData:
    ccy: str = ""
    cash_bal: float = 0
    u_time: int = 0

    @classmethod
    def init_from_json(cls, json_response):
        balance_data = BalanceData()
        balance_data.ccy = json_response.get("ccy")
        balance_data.cash_bal = float(json_response.get("cashBal"))
        balance_data.u_time = int(json_response.get("uTime"))
        return balance_data


@dataclass
class PosData:
    position_id: int = 0
    trade_id: str = ""
    inst_id: str = ""
    inst_type: InstType = None
    mgn_mode: MgnMode = None
    pos_side: PosSide = None
    pos: float = 0
    ccy: str = ""
    pos_ccy: str = ""
    avg_px: float = 0
    u_time: int = 0

    @classmethod
    def init_from_json(cls, json_response):
        position_data = PosData()
        position_data.position_id = int(json_response.get("posId"))
        position_data.trade_id = json_response.get("tradeId", "")
        position_data.inst_id = json_response.get("instId")
        position_data.inst_type = InstType[json_response.get("instType")]
        position_data.mgn_mode = MgnMode[json_response.get("mgnMode")]
        position_data.pos_side = PosSide[json_response.get("posSide")]
        position_data.pos = float(json_response.get("pos"))
        position_data.ccy = json_response.get("ccy")
        position_data.pos_ccy = json_response.get("posCcy")
        position_data.avg_px = float(json_response.get("avgPx"))
        position_data.u_time = json_response.get("uTime")
        return position_data


@dataclass
class BalanceAndPosition:
    p_time: int = 0
    balances: Dict[str, BalanceData] = field(default_factory=lambda: dict())
    positions: Dict[int, PosData] = field(default_factory=lambda: dict())

    @classmethod
    def init_from_json(cls, json_response):
        balance_and_position = BalanceAndPosition()
        balance_and_position.balances = {
            balance_data["ccy"]: BalanceData.init_from_json(balance_data)
            for balance_data in json_response["data"][0]["balData"]}
        balance_and_position.positions = {
            pos_data["posId"]: PosData.init_from_json(pos_data) for pos_data in json_response["data"][0]["posData"]}
        balance_and_position.p_time = int(json_response["data"][0]["pTime"])
        return balance_and_position

    def update_from_json(self, json_response):
        balance_data_list = json_response["data"][0]["balData"]
        pos_data_list = json_response["data"][0]["posData"]
        for balance_data in balance_data_list:
            balance = BalanceData.init_from_json(balance_data)
            if balance.cash_bal == 0 and balance.ccy in self.balances:
                del self.balances[balance.ccy]
            else:
                self.balances[balance.ccy] = balance
        for pos_data in pos_data_list:
            position = PosData.init_from_json(pos_data)
            if position.pos == 0 and position.position_id in self.positions:
                del self.positions[position.position_id]
            else:
                self.positions[position.position_id] = position


