from dataclasses import dataclass
from okx_market_maker.utils.OkxEnum import TdMode, OrderSide, OrderType, PosSide


@dataclass
class PlaceOrderRequest:
    inst_id: str
    td_mode: TdMode
    side: OrderSide
    ord_type: OrderType
    size: str
    pos_side: PosSide = None
    price: str = ""
    client_order_id: str = ""
    tag: str = ""
    reduce_only: bool = False
    tgt_ccy: str = ""
    ccy: str = ""

    def to_dict(self):
        return {
            "instId": self.inst_id, "tdMode": self.td_mode.value, "side": self.side.value,
            "ordType": self.ord_type.value, "sz": self.size, "ccy": self.ccy,
            "clOrdId": self.client_order_id, "tag": self.tag,
            "posSide": '' if not self.pos_side else self.pos_side.value,
            "px": '' if not self.price else str(self.price), "reduceOnly": self.reduce_only, "tgtCcy": self.tgt_ccy
        }


@dataclass
class AmendOrderRequest:
    inst_id: str
    order_id: str = ""
    client_order_id: str = ""
    req_id: str = ""
    cxl_on_fail: bool = False
    new_size: str = ""
    new_price: str = ""

    def to_dict(self):
        return {'instId': self.inst_id, 'cxlOnFail': self.cxl_on_fail, 'ordId': self.order_id,
                'clOrdId': self.client_order_id, 'reqId': self.req_id,
                'newSz': '' if not self.new_size else str(self.new_size),
                'newPx': '' if not self.new_price else str(self.new_price)}


@dataclass
class CancelOrderRequest:
    inst_id: str
    order_id: str = ""
    client_order_id: str = ""

    def to_dict(self):
        return {
            "instId": self.inst_id,
            "ordId": self.order_id,
            "clOrdId": self.client_order_id,
        }
