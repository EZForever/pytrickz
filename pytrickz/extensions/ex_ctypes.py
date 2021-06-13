'''
    Defines extension methods for `ctypes` primitive types (`c_int`, `c_long`, etc.).
'''

import operator
from ctypes import *
from typing import Any, Callable, Union

from .. import extension

_ctypes_signed_int_types = (
    c_int8,
    c_int16,
    c_int32,
    c_int64
)

_ctypes_unsigned_int_types = (
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64
)

_ctypes_int_types = (
    *_ctypes_signed_int_types,
    *_ctypes_unsigned_int_types
)

_unary_operators = {
    '__neg__': operator.neg,
    '__pos__': operator.pos,
    '__abs__': abs,
    '__invert__': operator.invert
}

_comparsion_operators = {
    '__lt__': operator.lt,
    '__le__': operator.le,
    '__eq__': operator.eq,
    '__ne__': operator.ne,
    '__ge__': operator.ge,
    '__gt__': operator.gt    
}

_arithmetic_operators = {
    '__add__': operator.add,
    '__sub__': operator.sub,
    '__mul__': operator.mul,
    #'__matmul__': operator.matmul,
    '__truediv__': operator.floordiv, #operator.truediv
    '__floordiv__': operator.floordiv,
    #'__divmod__': divmod,
    #'__pow__': pow,
    '__lshift__': operator.lshift,
    '__rshift__': operator.rshift,
    '__and__': operator.and_,
    '__xor__': operator.xor,
    '__or__': operator.or_
}

# Extending reflected operators is not supported by forbiddenfruit right now
#_reflected_arithmetic_operators = { k.replace('__', '__r', 1): v for k, v in _arithmetic_operators }

@extension(target = _ctypes_int_types, overwrite = True)
class ex_ctypes_int:
    # NOTE: Do not inherit from `c_int`, ctypes injects unwanted attributes otherwise

    def __unary(name: str, op: Callable) -> Callable:
        def __operator(self: c_int) -> c_int:
            '''
                Unary operators.
            '''
            return self.__class__(op(self.value))
        __operator.__name__ = name
        return __operator

    def __comparsion(name: str, op: Callable) -> Callable:
        def __operator(self: c_int, other: Union[c_int, int]) -> bool:
            '''
                Comparsion operators.
            '''
            return op(self.value, other.value if isinstance(other, _ctypes_int_types) else other)
        __operator.__name__ = name
        return __operator

    def __arithmetic(name: str, op: Callable) -> Callable:
        def __operator(self: c_int, other: Union[c_int, int]) -> Any:
            '''
                Arithmetic operators.
            '''
            if isinstance(other, _ctypes_int_types):
                other_value = other.value
                if sizeof(self) > sizeof(other) or (sizeof(self) == sizeof(other) and isinstance(self, _ctypes_unsigned_int_types)):
                    result_type = self.__class__
                else:
                    result_type = other.__class__
            else:
                other_value = other
                result_type = self.__class__
            return result_type(op(self.value, other_value))
        __operator.__name__ = name
        return __operator

    # ---

    for k, v in _unary_operators.items():
        locals()[k] = __unary(k, v)
    for k, v in _comparsion_operators.items():
        locals()[k] = __comparsion(k, v)
    for k, v in _arithmetic_operators.items():
        locals()[k] = __arithmetic(k, v)
    
    del k, v

