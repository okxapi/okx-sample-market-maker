from okx_market_maker.strategy.SampleMM import SampleMM
from okx_market_maker.market_data_service.WssMarketDataService import WssMarketDataService
from okx_market_maker.order_management_service.WssOrderManagementService import WssOrderManagementService
from okx_market_maker.position_management_service.WssPositionManagementService import WssPositionManagementService
from okx_market_maker.settings import TRADING_INSTRUMENT_ID, IS_PAPER_TRADING
from okx_market_maker.market_data_service.RESTMarketDataService import RESTMarketDataService


if __name__ == "__main__":
    mds = WssMarketDataService(
        url="wss://ws.okx.com:8443/ws/v5/public?brokerId=9999" if IS_PAPER_TRADING
        else "wss://ws.okx.com:8443/ws/v5/public",
        inst_id=TRADING_INSTRUMENT_ID,
        level=5,
        channel="books"
    )
    mds.start()
    rest_mds = RESTMarketDataService()
    oms = WssOrderManagementService(
        url="wss://ws.okx.com:8443/ws/v5/private?brokerId=9999" if IS_PAPER_TRADING
        else "wss://ws.okx.com:8443/ws/v5/private")
    oms.start()
    pms = WssPositionManagementService(
        url="wss://ws.okx.com:8443/ws/v5/private?brokerId=9999" if IS_PAPER_TRADING
        else "wss://ws.okx.com:8443/ws/v5/private")
    pms.start()
    strategy = SampleMM()
    rest_mds.start()
    mds.run_service()
    oms.run_service()
    pms.run_service()
    strategy.run()

