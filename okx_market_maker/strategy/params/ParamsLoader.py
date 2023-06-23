import traceback
import yaml

from okx_market_maker.settings import PARAMS_PATH


class ParamsLoader:
    def __init__(self):
        self.params = dict()
        self._inited = False

    def load_params(self) -> None:
        try:
            with open(PARAMS_PATH, 'r') as file:
                params = yaml.safe_load(file)
            self.params = params
        except:
            print(traceback.format_exc())

    def get_strategy_params(self, *args):
        if not self._inited:
            self.load_params()
        strategy_params = self.params.get("strategy")
        for arg in args:
            strategy_params = strategy_params.get(arg)
            if strategy_params is None:
                return
        return strategy_params
