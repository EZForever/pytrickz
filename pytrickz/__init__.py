'''
    A library aimed for providing handy hacks for your daily coding task.

    ```
    from pytrickz import *

    @extension
    def my_reversed(self: str) -> str:
        return self[ : : -1]
    print('123456'.my_reversed()) # 654321
    
    print(stream.range(3).map(lambda x: x + 1).reverse().to(tuple)) # (3, 2, 1)
    ```
'''

from .stream import stream
from .extension import extension

__all__ = [
    'iterables',
    'typevars',
    'stream',
    'extension'
]

