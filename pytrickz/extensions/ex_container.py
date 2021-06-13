'''
    Defines extension methods for container types (`list`, `tuple`, `dict`, etc.).
'''

from typing import Container

from .. import extension, stream
from ..typevars import *

_container_types = (
    list,
    tuple,
    dict,
    set,
    frozenset,
    bytes,
    bytearray
)

@extension(target = _container_types)
class ex_container(Container[T]):
    def stream(self) -> stream[T]:
        '''
            Construct an reentrant `stream` backed by this container. Equivalent to `stream(self)`.

            >>> [1, 2, 3].stream().to(tuple)
            (1, 2, 3)
        '''
        return stream(self)

