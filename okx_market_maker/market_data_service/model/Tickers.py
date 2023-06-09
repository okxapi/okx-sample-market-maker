from dataclasses import dataclass, field
from typing import Dict

from okx_market_maker.utils.OkxEnum import InstType


@dataclass
class Ticker:
    inst_type: InstType
    inst_id: str
    last: float = 0
    last_sz: float = 0
    ask_px: float = 0
    ask_sz: float = 0
    bid_px: float = 0
    bid_sz: float = 0
    open24h: float = 0
    high24h: float = 0
    low24h: float = 0
    vol_ccy24h: float = 0
    vol24h: float = 0
    sod_utc0: float = 0
    sod_utc8: float = 0
    ts: int = 0

    @classmethod
    def init_from_json(cls, json_response):
        """
        :param json_response:
         {
        "instType":"SWAP",
        "instId":"LTC-USD-SWAP",
        "last":"9999.99",
        "lastSz":"0.1",
        "askPx":"9999.99",
        "askSz":"11",
        "bidPx":"8888.88",
        "bidSz":"5",
        "open24h":"9000",
        "high24h":"10000",
        "low24h":"8888.88",
        "volCcy24h":"2222",
        "vol24h":"2222",
        "sodUtc0":"0.1",
        "sodUtc8":"0.1",
        "ts":"1597026383085"
        },
        :return: Ticker()
        """
        inst_type = InstType(json_response["instType"])
        inst_id = json_response["instId"]
        ticker = Ticker(inst_type, inst_id)
        ticker.last = float(json_response["last"]) if json_response.get("last") else 0
        ticker.last_sz = float(json_response["lastSz"]) if json_response.get("lastSz") else 0
        ticker.ask_px = float(json_response["askPx"]) if json_response.get("askPx") else 0
        ticker.ask_sz = float(json_response["askSz"]) if json_response.get("askSz") else 0
        ticker.bid_px = float(json_response["bidPx"]) if json_response.get("bidPx") else 0
        ticker.bid_sz = float(json_response["bidSz"]) if json_response.get("bidSz") else 0
        ticker.open24h = float(json_response["open24h"]) if json_response.get("open24h") else 0
        ticker.high24h = float(json_response["high24h"]) if json_response.get("high24h") else 0
        ticker.low24h = float(json_response["low24h"]) if json_response.get("low24h") else 0
        ticker.vol_ccy24h = float(json_response["volCcy24h"]) if json_response.get("volCcy24h") else 0
        ticker.vol24h = float(json_response["vol24h"]) if json_response.get("vol24h") else 0
        ticker.sod_utc0 = float(json_response["sodUtc0"]) if json_response.get("sodUtc0") else 0
        ticker.sod_utc8 = float(json_response["sodUtc8"]) if json_response.get("sodUtc8") else 0
        ticker.ts = int(json_response["ts"]) if json_response.get("ts") else 0
        return ticker

    def update_from_json(self, json_response):
        self.last = float(json_response["last"]) if json_response.get("last") else 0
        self.last_sz = float(json_response["lastSz"]) if json_response.get("lastSz") else 0
        self.ask_px = float(json_response["askPx"]) if json_response.get("askPx") else 0
        self.ask_sz = float(json_response["askSz"]) if json_response.get("askSz") else 0
        self.bid_px = float(json_response["bidPx"]) if json_response.get("bidPx") else 0
        self.bid_sz = float(json_response["bidSz"]) if json_response.get("bidSz") else 0
        self.open24h = float(json_response["open24h"]) if json_response.get("open24h") else 0
        self.high24h = float(json_response["high24h"]) if json_response.get("high24h") else 0
        self.low24h = float(json_response["low24h"]) if json_response.get("low24h") else 0
        self.vol_ccy24h = float(json_response["volCcy24h"]) if json_response.get("volCcy24h") else 0
        self.vol24h = float(json_response["vol24h"]) if json_response.get("vol24h") else 0
        self.sod_utc0 = float(json_response["sodUtc0"]) if json_response.get("sodUtc0") else 0
        self.sod_utc8 = float(json_response["sodUtc8"]) if json_response.get("sodUtc8") else 0
        self.ts = int(json_response["ts"]) if json_response.get("ts") else 0


@dataclass
class Tickers:
    _ticker_map: Dict[str, Ticker] = field(default_factory=lambda: dict())

    def update_from_json(self, json_response):
        if json_response.get("code") != '0':
            raise ValueError(f"Unsuccessful ticker response {json_response}")
        data = json_response["data"]
        for info in data:
            inst_id = info["instId"]
            if inst_id not in self._ticker_map:
                self._ticker_map[inst_id] = Ticker.init_from_json(info)
            else:
                self._ticker_map[inst_id].update_from_json(info)

    def get_ticker_by_inst_id(self, inst_id: str) -> Ticker:
        return self._ticker_map.get(inst_id)

    def get_usdt_price_by_ccy(self, ccy: str, use_mid: bool = True) -> float:
        if ccy == "USDT":
            return 1
        # 1. if ccy-USDT inst_id exists
        if f"{ccy}-USDT" in self._ticker_map:
            ticker = self.get_ticker_by_inst_id(f"{ccy}-USDT")
            return ((ticker.ask_px + ticker.bid_px) / 2) if use_mid else ticker.last
        # 2. if ccy-quote and quote-USDT inst_id exists
        for quote in ["USDC", "BTC", "ETH", "DAI", "OKB", "DOT", "EURT"]:
            if f"{ccy}-{quote}" in self._ticker_map and f"{quote}-USDT" in self._ticker_map:
                ticker = self.get_ticker_by_inst_id(f"{ccy}-{quote}")
                quote_ticker = self.get_ticker_by_inst_id(f"{quote}-USDT")
                return (((ticker.ask_px + ticker.bid_px) / 2) * ((quote_ticker.ask_px + quote_ticker.bid_px) / 2)) \
                    if use_mid else (ticker.last * quote_ticker.last)
        # 3. if neither case then return 0
        return 0
