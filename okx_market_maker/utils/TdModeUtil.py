from okx_market_maker.utils.OkxEnum import AccountConfigMode, InstType, TdMode
from okx_market_maker.settings import TRADING_MODE


class TdModeUtil:
    @classmethod
    def decide_trading_mode(cls, account_config: AccountConfigMode, inst_type: InstType,
                            td_mode_setting: str = TRADING_MODE) -> TdMode:
        """
        Trade Mode, when placing an order, you need to specify the trade mode.
        Non-margined:
        - SPOT and OPTION buyer: cash
        Single-currency margin account:
        - Isolated MARGIN: isolated
        - Cross MARGIN: cross
        - Cross SPOT: cash
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
        :param account_config:
        :param inst_type:
        :param td_mode_setting:
        :return:
        """
        if account_config == AccountConfigMode.CASH:
            if inst_type not in [InstType.SPOT, InstType.OPTION]:
                raise ValueError(f"Invalid inst type {inst_type} in Cash Mode!")
            return TdMode.CASH
        if account_config == AccountConfigMode.SINGLE_CCY_MARGIN:
            if td_mode_setting in TdMode:
                assigned_trading_mode = TdMode(td_mode_setting)
                if inst_type not in [InstType.SPOT, InstType.MARGIN] and assigned_trading_mode == TdMode.CASH:
                    return TdMode.CROSS
                if inst_type == InstType.SPOT:
                    return TdMode.CASH
                return assigned_trading_mode
            if inst_type == InstType.SPOT:
                return TdMode.CASH
            return TdMode.CROSS
        if account_config in [AccountConfigMode.MULTI_CCY_MARGIN, AccountConfigMode.PORTFOLIO_MARGIN]:
            if td_mode_setting in TdMode:
                assigned_trading_mode = TdMode(td_mode_setting)
                if assigned_trading_mode == TdMode.CASH:
                    return TdMode.CROSS
                if inst_type == InstType.MARGIN:
                    return TdMode.ISOLATED
                if inst_type == InstType.SPOT:
                    return TdMode.CROSS
                return assigned_trading_mode
            if inst_type == InstType.MARGIN:
                return TdMode.ISOLATED
            return TdMode.CROSS
        raise ValueError(f"Invalid Account config mode {account_config}!")
