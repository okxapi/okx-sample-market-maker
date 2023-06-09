import os

# api key credential
API_KEY = ""
API_KEY_SECRET = ""
API_PASSPHRASE = ""
IS_PAPER_TRADING = True

# market-making instrument
TRADING_INSTRUMENT_ID = "BTC-USDT-SWAP"

# default latency tolerance level
ORDER_BOOK_DELAYED_SEC = 5
ACCOUNT_DELAYED_SEC = 5

# risk-free ccy
RISK_FREE_CCY_LIST = ["USDT", "USDC", "DAI"]

# params yaml path
PARAMS_PATH = os.path.abspath(os.path.dirname(__file__) + "/params.yaml")
