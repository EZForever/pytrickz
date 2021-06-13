'''
    Defines several common type varibles for usage in type hints.

    ```
    from typing import Generic
    from pytrickz.typevars import *

    class MyMap(Generic[K, V]):
        pass
    ```
'''

from typing import TypeVar

T = TypeVar('T')
U = TypeVar('U')
K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')

