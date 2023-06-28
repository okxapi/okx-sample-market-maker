import os

# api key credential
API_KEY = ""
API_KEY_SECRET = ""
API_PASSPHRASE = ""
IS_PAPER_TRADING = True

# market-making instrument
TRADING_INSTRUMENT_ID = "BTC-USDT-SWAP"
TRADING_MODE = "cross"  # "cash" / "isolated" / "cross"

# default latency tolerance level
ORDER_BOOK_DELAYED_SEC = 60  # Warning if OrderBook not updated for these seconds, potential issues from wss connection
ACCOUNT_DELAYED_SEC = 60  # Warning if Account not updated for these seconds, potential issues from wss connection

# risk-free ccy
RISK_FREE_CCY_LIST = ["USDT", "USDC", "DAI"]

# params yaml path
PARAMS_PATH = os.path.abspath(os.path.dirname(__file__) + "/params.yaml")
