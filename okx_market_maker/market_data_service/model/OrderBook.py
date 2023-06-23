from dataclasses import field, dataclass
from typing import List
import binascii


@dataclass
class OrderBookLevel:
    price: float
    quantity: float
    order_count: int
    price_string: str
    quantity_string: str
    order_count_string: str

    @staticmethod
    def _is_valid_operand(other):
        return (hasattr(other, "price") and
                hasattr(other, "quantity"))

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.price < other.price

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.price == other.price


@dataclass
class OrderBook:
    inst_id: str
    _bids: List[OrderBookLevel] = field(default_factory=lambda: list())
    _asks: List[OrderBookLevel] = field(default_factory=lambda: list())
    timestamp: int = 0
    exch_check_sum: int = 0

    def set_bids_on_snapshot(self, order_book_level_list: List[OrderBookLevel]):
        self._bids = sorted(order_book_level_list, reverse=True)

    def set_asks_on_snapshot(self, order_book_level_list: List[OrderBookLevel]):
        self._asks = sorted(order_book_level_list, reverse=False)

    def set_bids_on_update(self, order_book_level: OrderBookLevel):
        if not self._bids or self._bids[-1] > order_book_level:
            self._bids.append(order_book_level)
        else:
            for i in range(len(self._bids)):
                if order_book_level > self._bids[i]:
                    self._bids.insert(i, order_book_level)
                    break
                elif order_book_level == self._bids[i]:
                    if order_book_level.quantity == 0:
                        self._bids.pop(i)
                    else:
                        self._bids[i] = order_book_level
                    break

    def set_asks_on_update(self, order_book_level: OrderBookLevel):
        if not self._asks or self._asks[-1] < order_book_level:
            self._asks.append(order_book_level)
        else:
            for i in range(len(self._asks)):
                if order_book_level < self._asks[i]:
                    self._asks.insert(i, order_book_level)
                    break
                elif order_book_level == self._asks[i]:
                    if order_book_level.quantity == 0:
                        self._asks.pop(i)
                    else:
                        self._asks[i] = order_book_level
                    break

    def set_timestamp(self, timestamp: int):
        self.timestamp = timestamp

    def set_exch_check_sum(self, checksum: int):
        self.exch_check_sum = checksum

    def _current_check_sum(self):
        bid_ask_string = ""
        for i in range(max(len(self._bids), len(self._asks))):
            if len(self._bids) > i:
                bid_ask_string += f"{self._bids[i].price_string}:{self._bids[i].quantity_string}:"
            if len(self._asks) > i:
                bid_ask_string += f"{self._asks[i].price_string}:{self._asks[i].quantity_string}:"
            if i + 1 >= 25:
                break
        if bid_ask_string:
            bid_ask_string = bid_ask_string[:-1]
        crc = binascii.crc32(bid_ask_string.encode()) & 0xffffffff  # Calculate CRC32 as unsigned integer
        crc_signed = crc if crc < 0x80000000 else crc - 0x100000000  # Convert to signed integer
        return crc_signed

    def do_check_sum(self) -> bool:
        if not self.exch_check_sum:
            return True  # ignore check sum
        current_crc = self._current_check_sum()
        return current_crc == self.exch_check_sum

    def _check_empty_array(self, order_book_array):
        if not order_book_array:
            raise IndexError(f"Orderbook for {self.inst_id}: either bids or asks array not initiated.")

    def best_bid(self) -> OrderBookLevel:
        self._check_empty_array(self._bids)
        return self._bids[0]

    def best_ask(self) -> OrderBookLevel:
        self._check_empty_array(self._asks)
        return self._asks[0]

    def best_bid_price(self) -> float:
        self._check_empty_array(self._bids)
        return self._bids[0].price

    def best_ask_price(self) -> float:
        self._check_empty_array(self._asks)
        return self._asks[0].price

    def bid_by_level(self, level: int) -> OrderBookLevel:
        self._check_empty_array(self._bids)
        if level <= 0:
            level = 1
        if level > len(self._bids):
            level = 0
        return self._bids[level - 1]

    def ask_by_level(self, level: int) -> OrderBookLevel:
        self._check_empty_array(self._asks)
        if level <= 0:
            level = 1
        if level > len(self._asks):
            level = 0
        return self._asks[level - 1]

    def middle_price(self):
        self._check_empty_array(self._bids)
        self._check_empty_array(self._asks)
        return (self._bids[0].price + self._asks[0].price) / 2
