from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskSnapShot:
    timestamp: int = 0

    asset_usdt_value: float = 0
    price_to_usdt_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_cash_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_loan_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
    asset_instrument_value_snapshot: Dict[str, float] = field(default_factory=lambda: dict())

    delta_usdt_value: float = 0
    delta_instrument_snapshot: Dict[str, float] = field(default_factory=lambda: dict())
