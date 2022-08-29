from dataclasses import dataclass
from inspect import getfullargspec
from typing import Optional, Type, ClassVar, Callable, Sequence, get_type_hints, List

__all__ = [
    'get_callable_arg_types',
    'AutoCastFail',
    'convert_args_to_function_parameter_types',
    'AutoCastError',
    'Param',
    'AutoCastHandler',
]


@dataclass(frozen=True)
class Param:
    name: str
    annotation: Type
    type: str

    POSITIONAL: ClassVar[str] = 'positional'
    VARARGS: ClassVar[str] = 'varargs'


def get_callable_arg_types(function, skip_self=True) -> Optional[List[Param]]:
    try:
        fullspec = getfullargspec(function)
        typehints = get_type_hints(function)
    except TypeError:
        return None

    getparamtype = lambda param: typehints.get(param, None) or fullspec.annotations.get(param, None)

    types = [Param(param, getparamtype(param), Param.POSITIONAL) for param in fullspec.args]
    # skipping self/cls is important when dealing with ModCommands, and other bound methods.
    # and also basic command functions as well
    # reason for this is when checking required positional arguments count, as both `self/cls` and `msg` are included in that count otherwise
    if skip_self and types and types[0].name.casefold() in ('self', 'cls'):
        types = types[1:]

    if fullspec.varargs is not None:
        types.append(Param('*' + fullspec.varargs, getparamtype(fullspec.varargs), Param.VARARGS))

    return types


@dataclass(frozen=True)
class AutoCastFail:
    value: str
    param: Param
    reason: Optional[str] = None
    exception: Optional[Exception] = None


class AutoCastError(Exception):
    def __init__(self, reason: Optional[str] = None, send_reason_to_chat: bool = False):
        super().__init__(reason)
        self.send_reason_to_chat = send_reason_to_chat
        self.reason: Optional[str] = reason


def _cast_arg_to_type(arg, param: Param):
    converter = getattr(param.annotation, '_handle_auto_cast', param.annotation)
    try:
        return converter(arg)
    except Exception as e:
        reason = None
        if isinstance(e, AutoCastError):
            reason = e.reason
        return AutoCastFail(exception=e, value=arg, param=param, reason=reason)


class AutoCastHandler:
    @classmethod
    def _handle_auto_cast(cls, value: str):
        pass


def convert_args_to_function_parameter_types(function: Callable, args: Sequence[str]):
    from ..message import Message
    types = get_callable_arg_types(function, skip_self=True)

    # ensure parameters are typed as Message are ignored, message is automatically passed to the command before any args are
    for i in range(len(types) - 1, -1, -1):
        if types[i].annotation == Message:
            del types[i]

    out_args = []
    i = 0

    for arg, param in zip(args, types):
        if param.type == Param.POSITIONAL:
            if param.annotation is not None:
                out_args.append(_cast_arg_to_type(arg, param))
            else:
                out_args.append(arg)
            i += 1

    vararg_type = next((p for p in types if p.type == Param.VARARGS), None)
    if vararg_type is not None:
        if vararg_type.annotation is not None:
            out_args.extend(map(lambda x: _cast_arg_to_type(x, vararg_type), args[i:]))
        else:
            out_args.extend(args[i:])

    return out_args

# """FullArgSpec(
#     args=['a', 'b'],
#     varargs='args',
#     varkw='kwargs',
#     defaults=None,
#     kwonlyargs=[],
#     kwonlydefaults=None,
#     annotations={'a': 'int', 'b': 'int', 'args': 'None', 'kwargs': 'str'}
# )"""
