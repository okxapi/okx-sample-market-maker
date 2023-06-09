from dataclasses import dataclass


@dataclass
class StrategyMeasurement:
    net_filled_qty: float = 0
    buy_filled_qty: float = 0
    sell_filled_qty: float = 0
    trading_volume: float = 0
