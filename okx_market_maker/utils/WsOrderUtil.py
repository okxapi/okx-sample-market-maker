from okx.websocket.WsUtils import isNotBlankStr, getParamKey, initSubscribeSet
from okx_market_maker.utils.OkxEnum import OrderOp

import shortuuid


def get_request_uuid(op):
    return f"{op}{str(shortuuid.uuid())}"


def check_socket_request_params(op: str, args: list, channel_args, channel_param_map):
    if ~isNotBlankStr(op):
        raise ValueError("op must not none")
    if op not in OrderOp:
        raise ValueError(f"invalid op {op}")
    request_id = get_request_uuid(op)
    for arg in args:
        channel = arg['channel'].strip()
        if ~isNotBlankStr(channel):
            raise ValueError("channel must not none")
        arg_set = channel_param_map.get(channel, set())
        arg_key = getParamKey(arg)
        if arg_key in arg_set:
            continue
        else:
            valid_params = initSubscribeSet(arg)
        if len(valid_params) < 1:
            continue
        p = {}
        for k in arg:
            p[k.strip()] = arg.get(k).strip()
        channel_param_map[channel] = channel_param_map.get(channel, set()) | valid_params
        if channel not in channel_args:
            channel_args[channel] = []
        channel_args[channel].append(p)


def get_request_param_key(arg: dict) -> str:
    s = ""
    for k in arg:
        if k == 'channel':
            continue
        s = s + "@" + arg.get(k)
    return s


def init_request_set(arg: dict) -> set:
    params_set = set()
    if arg is None:
        return params_set
    elif isinstance(arg, dict):
        params_set.add(get_request_param_key(arg))
        return params_set
    else:
        raise ValueError("arg must dict")
