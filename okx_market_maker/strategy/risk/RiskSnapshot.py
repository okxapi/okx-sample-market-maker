from dataclasses import dataclass, field
from typing import Dict

from okx_market_maker.market_data_service.model.Instrument import Instrument


@dataclass
class AssetValueInst:
    instrument: Instrument = None
    asset_value: float = 0
    pos: float = 0
    mark_px: float = 0
    avg_px: float = 0
    liability: float = 0
    pos_ccy: str = ""
    ccy: str = ""
    margin: float = 0


@dataclass
class RiskSnapShot:
    timestamp: int = 0

    asset_usd_value: float = 0
    price_to_usd_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_cash_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_loan_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_instrument_value_snapshot: Dict[str, AssetValueInst] = field(default_factory=lambda: dict())
    mark_px_instrument_snapshot: Dict[str, float] = field(default_factory=lambda: dict())

    delta_usd_value: float = 0
    delta_instrument_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
