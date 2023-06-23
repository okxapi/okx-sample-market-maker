from dataclasses import dataclass
from enum import Enum
from okx_market_maker.utils.OkxEnum import OrderSide, OrderType


class StrategyOrderStatus(Enum):
    SENT = "sent"
    ACK = "ack"
    CXL_SENT = 'cxl_sent'
    CXL_ACK = 'cxl_ack'
    AMD_SENT = 'amd_sent'
    AMD_ACK = 'amd_ack'
    CANCELED = "canceled"
    FILLED = "filled"
    LIVE = "live"
    PARTIALLY_FILLED = "partially_filled"


@dataclass
class StrategyOrder:
    inst_id: str
    side: OrderSide
    ord_type: OrderType
    size: str
    price: str = ""
    client_order_id: str = ""
    order_id: str = ""
    strategy_order_status: StrategyOrderStatus = StrategyOrderStatus.SENT
    tgt_ccy: str = ""
    amend_req_id: str = ""
    filled_size: str = "0"
    avg_fill_price: float = 0

    def __eq__(self, other):
        return (self.side == other.side) and (self.inst_id == other.inst_id) \
               and (self.size == other.size) and (self.price == other.price) and (self.ord_type == other.ord_type)

    def get_id(self):
        return f"{self.inst_id}-{self.ord_type.value}-{self.side.value}-{self.size}@{self.price}"
