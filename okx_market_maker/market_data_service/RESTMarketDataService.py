import logging
import threading
import time
import traceback

from okx.exceptions import OkxAPIException, OkxParamsException, OkxRequestException
from okx.MarketData import MarketAPI
from okx.PublicData import PublicAPI
from okx_market_maker.market_data_service.model.MarkPx import MarkPxCache
from okx_market_maker.settings import IS_PAPER_TRADING
from okx_market_maker import tickers_container, mark_px_container
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.utils.OkxEnum import InstType


class RESTMarketDataService(threading.Thread):
    def __init__(self, is_paper_trading=IS_PAPER_TRADING):
        super().__init__()
        self.market_api = MarketAPI(flag='0' if not is_paper_trading else '1', debug=False)
        self.public_api = PublicAPI(flag='0' if not is_paper_trading else '1', debug=False)
        if not tickers_container:
            tickers_container.append(Tickers())
        if not mark_px_container:
            mark_px_container.append(MarkPxCache())

    def run(self) -> None:
        while 1:
            try:
                json_response = self.market_api.get_tickers(instType=InstType.SPOT.value)
                tickers: Tickers = tickers_container[0]
                tickers.update_from_json(json_response)
                mark_px_cache: MarkPxCache = mark_px_container[0]
                json_response = self.public_api.get_mark_price(instType=InstType.MARGIN.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.SWAP.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.FUTURES.value)
                mark_px_cache.update_from_json(json_response)
                json_response = self.public_api.get_mark_price(instType=InstType.OPTION.value)
                mark_px_cache.update_from_json(json_response)
                time.sleep(2)
            except KeyboardInterrupt:
                break
            except (OkxAPIException, OkxParamsException, OkxRequestException):
                logging.warning(traceback.format_exc())
                time.sleep(10)


if __name__ == "__main__":
    rest_mds = RESTMarketDataService()
    rest_mds.start()
