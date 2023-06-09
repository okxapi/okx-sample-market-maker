# okx-sample-market-maker

## Overview
This is an unofficial sample Python market marker using [OKX V5 API](https://www.okx.com/docs-v5/en/#overview), based on the [OKX V5 API PYTHON SDK](https://github.com/okxapi/python-okx).

The goal of this project is to provide one of the solution for users to build a proper trading system that can subscribe market data updates, order updates and account and position updates in a precise and timely manner, send order operation requests based on strategy ideas and through the order management process, and write arbitrary customized strategy logic on the top of the trading system. The aim of this project is purely for exhibition or research purpose. Users are strongly recommended to use [DEMO TRADING ENVIRONMENT](https://www.okx.com/docs-v5/en/#overview-demo-trading-services) for any development. This project should not guarantee any PNL seeking strategy or liquidity providing obligation. 

This project is not related to the OKX Trading Bots features. To get access to multiple strategies that can help you trade at ease, please refer to [OKX Trading Bots](https://www.okx.com/trading-bot).

## Getting Started
### Prerequisites
```python version：>=3.9```
```WebSocketAPI： websockets package advise version 6.0```
```python-okx>=0.1.9```
```autobahn~=23.1.2```
```shortuuid~=1.0.11```
```Twisted~=22.10.0```
```PyYAML~=6.0```

### Quick Start
1. Git clone this project to your local development environment. Click the Code button on the top-right of the page, and follow the instruction to git clone the project.
2. Open the project folder okx-sample-market-maker. Install the dependency by command ```pip install -r requirements.txt```. Creating a python virtual environment using ```virtualenv``` is strongly recommended.
3. Switch to demo trading mode in your OKX account. Generate a DEMO Trading API key under demo trading mode. For the introduction to OKX demo trading environment, please refer to [How to Practice Trading Crypto on OKX](https://www.okx.com/learn/how-to-practice-trading-crypto-on-okx-with-demo-trading).
4. Put your API key credentials into ```okx_market_market/settings.py```, in the section of  ```API_KEY```, ```API_SECRET_KEY```, and ```API_SECRET_KEY```. It is recommended to set ```IS_PAPER_TRADING```  as True.
5. The ```TRADING_INSTRUMENT_ID``` in ```okx_market_market/settings.py``` by default is set as BTC-USDT-SWAP. If you want to trade on other symbol, feel free the change this field. To fetch the valid Instrument ID, please refer to [OKX Public API](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-instruments).
6. ```okx_market_market/params.yaml``` stores a set of strategy parameters that could be dynamic loaded during the strategy run-time. Make sure you review these parameters before hit the running button. Some parameters like ```single_order_size``` is instrument-related so will need users own judgement.
7. HIT THE RUN BUTTON! Run the sample market maker by running the main script ```okx_market_market/run_sample_market_maker.py``` from your IDE or from command line. From the command line you can simply run ```python3 okx_market_market/run_sample_market_maker.py```.

### Output
```PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26441.4
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26414.9
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26388.4
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26362.0
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26335.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26494.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26521.0
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26547.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26573.9
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26600.4
===========  Strategy Summary  ==============
StrategyMeasurement(net_filled_qty=0, buy_filled_qty=0, sell_filled_qty=0, trading_volume=0)
RiskSnapShot(timestamp=1686295200410, asset_usdt_value=71419.53896952674, price_to_usdt_snapshot={'BTC': 26473.95, 'ETH': 1834.585, 'OKB': 44.825, 'JFI': 39.254999999999995, 'USDC': 0.99995, 'USDK': 0, 'TUSD': 0.668425, 'PAX': 0.8250500000000001, 'USDT': 1, 'UNI': 4.5825, 'LTC': 87.465, 'TRX': 0.07739499999999999, 'ADA': 0.31515}, asset_cash_snapshot={'BTC': 1.0010389610816628, 'ETH': 4.590149026394265, 'OKB': 100.0, 'JFI': 100.0, 'USDC': 3000.0, 'USDK': 3000.0, 'TUSD': 3000.0, 'PAX': 3000.0, 'USDT': 2684.1423424698123, 'UNI': 500.0, 'LTC': 10.0, 'TRX': 10000.0, 'ADA': 1000.0}, asset_loan_snapshot={}, asset_instrument_value_snapshot={'BTC-USDT-SWAP|net:BTC': 0.5163433364398406}, delta_usdt_value=51192.25860531541, delta_instrument_snapshot={'BTC-USDT-SWAP|net:BTC': -0.033})
AMEND ORDER orderaFZBngCqMjsxVHjDtD2TBC with new size 0 or new price 26444.7, req_id is amend9J9HQCeQbuCrRRDS4LLzpk
AMEND ORDER order7edCnqJf8LSaASr7aUF8Ep with new size 0 or new price 26418.2, req_id is amendhqggfxytoEgwZWRmGN4otE
AMEND ORDER orderSp6zyec6vk6reducoebAw8 with new size 0 or new price 26391.7, req_id is amendYnBrazuLpuzScAA4hcHkFd
AMEND ORDER order4xSjPPTyiCosUfX7M4dYcT with new size 0 or new price 26365.300000000003, req_id is amendaYCTkuci8VSUE4WqhCSuNt
AMEND ORDER order68zeuyF56N4NH6FqKsnHbU with new size 0 or new price 26338.800000000003, req_id is amendhupm2b54yQm92qab3oGzcw
AMEND ORDER orderL4mncCFYWPCagUEYQkxeuQ with new size 0 or new price 26497.800000000003, req_id is amendgEYsEvmbYt6yMVHsLNXs3X
AMEND ORDER orderTFLxbR9tTPLU8kE4HXxJ5w with new size 0 or new price 26524.300000000003, req_id is amend2AjcdkrPvbKWBSfnLr89Xx
AMEND ORDER orderVrGqNDiF2fiAj6J2Nedv4J with new size 0 or new price 26550.800000000003, req_id is amendTPLgHMPj25vfoh3kSaqdfB
AMEND ORDER ordermFnP2ZKhhkeK8YBw4M35cT with new size 0 or new price 26577.2, req_id is amendU5HC3greWaN6HqGvfQgLNN
AMEND ORDER orderEY4tUgAFzYtqea4qTbbTdC with new size 0 or new price 26603.7, req_id is amendJsqVtyBMp6pfsrrsR79kch
...
KeyboardInterrupt

CANCELING ORDER orderaFZBngCqMjsxVHjDtD2TBC
CANCELING ORDER order7edCnqJf8LSaASr7aUF8Ep
CANCELING ORDER orderSp6zyec6vk6reducoebAw8
CANCELING ORDER order4xSjPPTyiCosUfX7M4dYcT
CANCELING ORDER order68zeuyF56N4NH6FqKsnHbU
CANCELING ORDER orderL4mncCFYWPCagUEYQkxeuQ
CANCELING ORDER orderTFLxbR9tTPLU8kE4HXxJ5w
CANCELING ORDER orderVrGqNDiF2fiAj6J2Nedv4J
CANCELING ORDER ordermFnP2ZKhhkeK8YBw4M35cT
CANCELING ORDER orderEY4tUgAFzYtqea4qTbbTdC
```
