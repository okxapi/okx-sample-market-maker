# OKX Sample Market Maker

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
5. The ```TRADING_INSTRUMENT_ID``` in ```okx_market_market/settings.py``` by default is set as *BTC-USDT-SWAP* with ```TRADING_MODE``` as *cross*. If you want to trade on other symbol, feel free the change this field. To fetch the valid Instrument ID, please refer to [OKX Public API](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-instruments). Some valid InstId examples from OKX: ```BTC-USDT / BTC-USDT-SWAP / BTC-USDT-230630 / BTC-USD-230623-22000-C```. For the selection of Trading Mode (cash/isolated/cross), please refer to *Trading Instrument & Trading Mode* section below.
6. ```okx_market_market/params.yaml``` stores a set of strategy parameters that could be dynamic loaded during the strategy run-time. Make sure you review these parameters before hit the running button. Some parameters like ```single_size_as_multiple_of_lot_size``` is instrument-related so will need users own judgement.
7. HIT THE RUN BUTTON! Run the sample market maker by running the main script ```okx_market_maker/run_sample_market_maker.py``` from your IDE or from command line. From the command line you can simply run ```python3 -m okx_market_maker.run_sample_market_maker```.


### Trading Instrument & Trading Mode
```Trade Mode, when placing an order, you need to specify the trade mode.
Non-margined:
- SPOT and OPTION buyer: cash
Single-currency margin account:
- Isolated MARGIN: isolated
- Cross MARGIN: cross
- SPOT: cash
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
Multi-currency margin account:
- Isolated MARGIN: isolated
- Cross SPOT: cross
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
Portfolio margin:
- Isolated MARGIN: isolated
- Cross SPOT: cross
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
```

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
==== Risk Summary ====
Time: 2023-06-23 15:37:53
Inception: 2023-06-23 15:37:21
P&L since inception (USD): 10.89
Asset Value Change since inception (USD): -51.25
Trading Instrument: BTC-USDT-SWAP (SWAP)
Trading Instrument Exposure (BTC): -0.0060
Trading Instrument Exposure (USDT): -179.91
Net Traded Position: -6
Net Trading Volume: 18
==== End of Summary ====
AMEND ORDER orderaFZBngCqMjsxVHjDtD2TBC with new size 0 or new price 26444.7, req_id is amend9J9HQCeQbuCrRRDS4LLzpk
AMEND ORDER order7edCnqJf8LSaASr7aUF8Ep with new size 0 or new price 26418.2, req_id is amendhqggfxytoEgwZWRmGN4otE
AMEND ORDER orderSp6zyec6vk6reducoebAw8 with new size 0 or new price 26391.7, req_id is amendYnBrazuLpuzScAA4hcHkFd
AMEND ORDER order4xSjPPTyiCosUfX7M4dYcT with new size 0 or new price 26365.3, req_id is amendaYCTkuci8VSUE4WqhCSuNt
AMEND ORDER order68zeuyF56N4NH6FqKsnHbU with new size 0 or new price 26338.8, req_id is amendhupm2b54yQm92qab3oGzcw
AMEND ORDER orderL4mncCFYWPCagUEYQkxeuQ with new size 0 or new price 26497.8, req_id is amendgEYsEvmbYt6yMVHsLNXs3X
AMEND ORDER orderTFLxbR9tTPLU8kE4HXxJ5w with new size 0 or new price 26524.3, req_id is amend2AjcdkrPvbKWBSfnLr89Xx
AMEND ORDER orderVrGqNDiF2fiAj6J2Nedv4J with new size 0 or new price 26550.8, req_id is amendTPLgHMPj25vfoh3kSaqdfB
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
