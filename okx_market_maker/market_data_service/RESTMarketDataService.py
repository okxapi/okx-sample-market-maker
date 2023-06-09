import logging
import threading
import time
import traceback

from okx.exceptions import OkxAPIException, OkxParamsException, OkxRequestException
from okx.MarketData import MarketAPI
from okx_market_maker.settings import IS_PAPER_TRADING
from okx_market_maker import tickers_container
from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.utils.OkxEnum import InstType


class RESTMarketDataService(threading.Thread):
    def __init__(self):
        super().__init__()
        self.market_api = MarketAPI(flag='0' if not IS_PAPER_TRADING else '1', debug=False)
        if not tickers_container:
            tickers_container.append(Tickers())

    def run(self) -> None:
        while 1:
            try:
                json_response = self.market_api.get_tickers(instType=InstType.SPOT.value)
                tickers: Tickers = tickers_container[0]
                tickers.update_from_json(json_response)
                time.sleep(2)
            except KeyboardInterrupt:
                break
            except (OkxAPIException, OkxParamsException, OkxRequestException):
                logging.warning(traceback.format_exc())
                time.sleep(10)


if __name__ == "__main__":
    rest_mds = RESTMarketDataService()
    rest_mds.start()
