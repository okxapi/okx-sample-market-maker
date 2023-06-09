from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AccountDetail:
    avail_bal: float = 0
    avail_eq: float = 0
    ccy: str = ""
    cash_bal: float = 0
    u_time: int = 0
    dis_eq: float = 0
    eq: float = 0
    eq_usd: float = 0
    frozen_bal: float = 0
    interest: float = 0
    iso_eq: float = 0
    liability: float = 0
    max_loan: float = 0
    notional_lever: float = 0
    ord_frozen: float = 0
    upl: float = 0
    upl_liability: float = 0
    cross_liability: float = 0
    iso_liability: float = 0
    coin_usd_price: float = 0
    strategy_eq: float = 0
    spot_in_usd_amt: float = 0
    iso_upl: float = 0

    @classmethod
    def init_from_json(cls, json_response):
        account_detail = AccountDetail()
        account_detail.avail_bal = float(json_response["availBal"]) if json_response.get("availBal") else 0
        account_detail.avail_eq = float(json_response["availEq"]) if json_response.get("availEq") else 0
        account_detail.ccy = json_response["ccy"]
        account_detail.cash_bal = float(json_response["cashBal"]) if json_response.get("cashBal") else 0
        account_detail.u_time = int(json_response["uTime"]) if json_response.get("uTime") else 0
        account_detail.eq = float(json_response["eq"]) if json_response.get("eq") else 0
        account_detail.eq_usd = float(json_response["eqUsd"]) if json_response.get("eqUsd") else 0
        account_detail.frozen_bal = float(json_response["frozenBal"]) if json_response.get("frozenBal") else 0
        account_detail.interest = float(json_response["interest"]) if json_response.get("interest") else 0
        account_detail.iso_eq = float(json_response["isoEq"]) if json_response.get("isoEq") else 0
        account_detail.liability = float(json_response["liab"]) if json_response.get("liab") else 0
        account_detail.max_loan = float(json_response["maxLoan"]) if json_response.get("maxLoan") else 0
        account_detail.notional_lever = float(json_response["notionalLever"]) \
            if json_response.get("notionalLever") else 0
        account_detail.ord_frozen = float(json_response["ordFrozen"]) if json_response.get("ordFrozen") else 0
        account_detail.upl = float(json_response["upl"]) if json_response.get("upl") else 0
        account_detail.upl_liability = float(json_response["uplLiab"]) if json_response.get("uplLiad") else 0
        account_detail.cross_liability = float(json_response["crossLiab"]) if json_response.get("crossLiab") else 0
        account_detail.iso_liability = float(json_response["isoLiab"]) if json_response.get("isoLiab") else 0
        account_detail.coin_usd_price = float(json_response["coinUsdPrice"]) if json_response.get("coinUsdPrice") else 0
        account_detail.strategy_eq = float(json_response["stgyEq"]) if json_response.get("stgyEq") else 0
        account_detail.spot_in_usd_amt = float(json_response["spotInUseAmt"]) \
            if json_response.get("spotInUseAmt") else 0
        account_detail.iso_upl = float(json_response["isoUpl"]) if json_response.get("isoUpl") else 0
        return account_detail


@dataclass
class Account:
    u_time: int = 0
    total_eq: float = 0
    iso_eq: float = 0
    adj_eq: float = 0
    ord_frozen: float = 0
    imr: float = 0
    mmr: float = 0
    notional_usd: float = 0
    mgn_ratio: float = 0
    details: Dict[str, AccountDetail] = field(default_factory=lambda: list())

    @classmethod
    def init_from_json(cls, json_response):
        """
        :param json_response:
         {
          "arg": {
            "channel": "account",
            "uid": "77982378738415879"
          },
          "data": [
            {
              "uTime": "1614846244194",
              "totalEq": "91884.8502560037982063",
              "adjEq": "91884.8502560037982063",
              "isoEq": "0",
              "ordFroz": "0",
              "imr": "0",
              "mmr": "0",
              "notionalUsd": "",
              "mgnRatio": "100000",
              "details": [{
                  "availBal": "",
                  "availEq": "1",
                  "ccy": "BTC",
                  "cashBal": "1",
                  "uTime": "1617279471503",
                  "disEq": "50559.01",
                  "eq": "1",
                  "eqUsd": "45078.3790756226851775",
                  "frozenBal": "0",
                  "interest": "0",
                  "isoEq": "0",
                  "liab": "0",
                  "maxLoan": "",
                  "mgnRatio": "",
                  "notionalLever": "0.0022195262185864",
                  "ordFrozen": "0",
                  "upl": "0",
                  "uplLiab": "0",
                  "crossLiab": "0",
                  "isoLiab": "0",
                  "coinUsdPrice": "60000",
                  "stgyEq":"0",
                  "spotInUseAmt":"",
                  "isoUpl":""
                }
              ]
            }
          ]
        }
        :return:
        """
        data = json_response["data"][0]
        account = Account()
        account.u_time = int(data["uTime"]) if data.get("uTime") else 0
        account.total_eq = float(data["totalEq"]) if data.get("totalEq") else 0
        account.iso_eq = float(data["isoEq"]) if data.get("isoEq") else 0
        account.adj_eq = float(data["adjEq"]) if data.get("adjEq") else 0
        account.ord_frozen = float(data["ordFroz"]) if data.get("ordFroz") else 0
        account.imr = float(data["imr"]) if data.get("imr") else 0
        account.mmr = float(data["mmr"]) if data.get("mmr") else 0
        account.notional_usd = float(data["notionalUsd"]) if data.get("notionalUsd") else 0
        account.mgn_ratio = float(data["mgnRatio"]) if data.get("mgnRatio") else 0
        account.details = {detail_data["ccy"]: AccountDetail.init_from_json(detail_data)
                           for detail_data in data["details"]}
        return account

    def update_from_json(self, json_response):
        """
        Data pushed in regular interval: Only currencies with non-zero balance will be pushed.
        Definition of non-zero balance: any value of eq, availEq, availBql parameters is not 0.
        When the value of eq, availEq and availBql parameters are all zero, drop the detail of that ccy from Account
        :param json_response: same as init_from_json
        :return:
        """
        data = json_response["data"][0]
        self.u_time = int(data["uTime"]) if data.get("uTime") else 0
        self.total_eq = float(data["totalEq"]) if data.get("totalEq") else 0
        self.iso_eq = float(data["isoEq"]) if data.get("isoEq") else 0
        self.adj_eq = float(data["adjEq"]) if data.get("adjEq") else 0
        self.ord_frozen = float(data["ordFroz"]) if data.get("ordFroz") else 0
        self.imr = float(data["imr"]) if data.get("imr") else 0
        self.mmr = float(data["mmr"]) if data.get("mmr") else 0
        self.notional_usd = float(data["notionalUsd"]) if data.get("notionalUsd") else 0
        self.mgn_ratio = float(data["mgnRatio"]) if data.get("mgnRatio") else 0
        for detail_data in data["details"]:
            account_detail = AccountDetail.init_from_json(detail_data)
            if not account_detail.eq and not account_detail.avail_eq and not account_detail.avail_bal and \
                    account_detail.ccy in self.details:
                del self.details[account_detail.ccy]
                continue
            self.details[account_detail.ccy] = account_detail

    def get_account_details(self) -> Dict[str, AccountDetail]:
        return self.details
