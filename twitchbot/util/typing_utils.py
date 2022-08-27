from dataclasses import dataclass
from inspect import getfullargspec, ismethod
from typing import Optional, Type, ClassVar, Callable, Sequence, get_type_hints, List

__all__ = [
    'get_callable_arg_types',
    'AutoCastFail',
    'convert_args_to_function_parameter_types',
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
    if skip_self and ismethod(function):
        types = types[1:]

    if fullspec.varargs is not None:
        types.append(Param('*' + fullspec.varargs, getparamtype(fullspec.varargs), Param.VARARGS))

    return types


class AutoCastFail:
    def __init__(self, e, value: str, param: Param):
        self.param = param
        self.value = value
        self.e: Type[Exception] = e

    def __repr__(self):
        return f'<{self.__class__.__name__}: exception={self.e!r} value={self.value!r} param={self.param!r}>'


def _cast_arg_to_type(arg, param: Param):
    converter = getattr(param.annotation, '_handle_auto_cast', param.annotation)
    try:
        return converter(arg)
    except Exception as e:
        return AutoCastFail(e, arg, param)


def convert_args_to_function_parameter_types(function: Callable, args: Sequence[str]):
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

# """FullArgSpec(
#     args=['a', 'b'],
#     varargs='args',
#     varkw='kwargs',
#     defaults=None,
#     kwonlyargs=[],
#     kwonlydefaults=None,
#     annotations={'a': 'int', 'b': 'int', 'args': 'None', 'kwargs': 'str'}
# )"""
