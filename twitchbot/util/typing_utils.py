from typing import Optional, Type, ClassVar, Callable
from dataclasses import dataclass
from typing import get_type_hints
from inspect import getfullargspec, ismethod

__all__ = [
    'get_callable_arg_types',
    'AutoCastFail',
]


@dataclass(frozen=True)
class Param:
    name: str
    annotation: Type
    type: str

    POSITIONAL: ClassVar[str] = 'positional'
    VARARGS: ClassVar[str] = 'varargs'


def get_callable_arg_types(function, skip_self=True) -> Optional[list[Param]]:
    try:
        fullspec = getfullargspec(function)
        typehints = get_type_hints(function)
    except TypeError:
        return None

    getparamtype = lambda param: typehints.get(param, None) or fullspec.annotations.get(param, None)

    types = [Param(param, getparamtype(param), Param.POSITIONAL) for param in fullspec.args]
    if skip_self and ismethod(function):
        types = types[1:]

    if fullspec.varargs is not None:
        types.append(Param('*' + fullspec.varargs, getparamtype(fullspec.varargs), Param.VARARGS))

    return types


class AutoCastFail:
    def __init__(self, e, arg: str, param: Param):
        self.param = param
        self.arg = arg
        self.e: Type[Exception] = e

    def __repr__(self):
        return f'<{self.__class__.__name__}: exception={self.e!r} arg={self.arg!r} param={self.param!r}>'


def _cast_arg_to_type(arg, param: Param):
    converter = getattr(param.annotation, '_handle_auto_cast', param.annotation)
    try:
        return converter(arg)
    except Exception as e:
        return AutoCastFail(e, arg, param)


def process_arg_types(function: Callable, args: str):
    types = get_callable_arg_types(function, skip_self=True)
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


class C:
    def basic_command(self, z: int, b: float, c: float, *a: float):
        pass


process_arg_types(C().basic_command, ('1', '2', '6', 'testing'))
# """FullArgSpec(
#     args=['a', 'b'],
#     varargs='args',
#     varkw='kwargs',
#     defaults=None,
#     kwonlyargs=[],
#     kwonlydefaults=None,
#     annotations={'a': 'int', 'b': 'int', 'args': 'None', 'kwargs': 'str'}
# )"""
