from enum import Enum, EnumMeta


class InstType(Enum):
    MARGIN = "MARGIN"
    SWAP = "SWAP"
    FUTURES = "FUTURES"
    OPTION = "OPTION"
    SPOT = "SPOT"


class MgnMode(Enum):
    cross = "cross"
    isolated = "isolated"


class PosSide(Enum):
    long = "long"
    short = "short"
    net = "net"


class OptType(Enum):
    CALL = "C"
    PUT = "P"


class CtType(Enum):
    LINEAR = "linear"
    INVERSE = "inverse"


class InstState(Enum):
    LIVE = "live"
    SUSPEND = "suspend"
    PREOPEN = "preopen"
    TEST = "test"


class OrderCategory(Enum):
    normal = "normal"
    twap = "twap"
    adl = "adl"
    full_liquidation = "full_liquidation"
    partial_liquidation = "partial_liquidation"
    delivery = "delivery"
    ddh = "ddh"


class OrderExecType(Enum):
    TAKER = "T"
    MAKER = "M"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    POST_ONLY = "post_only"
    FOK = "fok"
    IOC = "ioc"
    OPTIMAL_LIMIT_IOC = "optimal_limit_ioc"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderState(Enum):
    CANCELED = "canceled"
    LIVE = "live"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"


class ListEnumMeta(EnumMeta):
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]


class OrderOp(Enum, metaclass=ListEnumMeta):
    ORDER = "order"
    BATCH_ORDER = "batch-orders"
    CANCEL = "cancel-order"
    BATCH_CANCEL = "batch-cancel-orders"
    AMEND = "amend-order"
    BATCH_AMEND = "batch-amend-order"


class TdMode(Enum, metaclass=ListEnumMeta):
    CASH = "cash"
    ISOLATED = "isolated"
    CROSS = "cross"


class AccountConfigMode(Enum, metaclass=ListEnumMeta):
    CASH = 1
    SINGLE_CCY_MARGIN = 2
    MULTI_CCY_MARGIN = 3
    PORTFOLIO_MARGIN = 4
