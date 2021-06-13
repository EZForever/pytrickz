'''
    `pytrickz.extensions` contains extension methods targeting built-in types.
    To enable the extensions for a type, the corresponding module must be imported at least once.

    Currently supported modules:
        - `ex_str`: `str`
        - `ex_bytes`: `bytes` and `bytearray`
        - `ex_ctypes`: `ctypes` primitive types (`c_int`, `c_long`, etc.)
        - `ex_container`: container types (`list`, `tuple`, `dict`, etc.)

    ```
    >>> from pytrickz.extensions import *
    >>> '313233343536'.unhex()
    b'123456'
    ```
'''

__all__ = [
    'ex_str',
    'ex_bytes',
    'ex_ctypes',
    'ex_container'
]

