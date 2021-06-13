'''
    Defines several handy `Iterable` classes.

    ```
    from pytrickz.iterables import iterate

    print(iterate(lambda x: x * 3, 1).stream().take(5)) # (1, 3, 9, 27, 81)
    ```
'''

from typing import Callable, Generic, Iterable, Iterator

from .stream import stream
from .typevars import *

class iterate(Generic[T]):
    '''
        An `Iterable` that iterates `func` over `seed`, i.e. `seed`, `func(seed)`, `func(func(seed))`, endlessly.
    
        >>> iterate(lambda x: x * 3, 1).stream().take(5)
        (1, 3, 9, 27, 81)
    '''

    class _iterator(Generic[T]):
        '''
            The underlying `Iterator` for `iterate`.
        '''

        def __init__(self, func: Callable[[T], T], initial: T):
            self.__func = func
            self.__val = initial
            self.__initial = True

        def __iter__(self) -> Iterator[T]:
            return self
        
        def __next__(self) -> T:
            if self.__initial:
                self.__initial = False
            else:
                self.__val = self.__func(self.__val)
            return self.__val

    def __init__(self, func: Callable[[T], T], initial: T):
        '''
            Construct a `Iterable` that iterates `func` over `seed`, i.e. `seed`, `func(seed)`, `func(func(seed))`, endlessly.

            >>> iterate(lambda x: x * 3, 1).stream().take(5)
            (1, 3, 9, 27, 81)
        '''
        self.__func = func
        self.__initial = initial
    
    def __iter__(self) -> Iterator[T]:
        '''
            Wrapper of `self.iter()` for usage in language constructs.
        '''
        return self.iter()

    def iter(self) -> Iterator[T]:
        '''
            Obtain an `Iterator` for usage in language constructs.
        '''
        return self._iterator(self.__func, self.__initial)

    def stream(self) -> stream[T]:
        '''
            Construct an infinite reentrant `stream` backed by this `iterate`. Equivalent to `stream(self)`.

            >>> iterate(lambda x: x * 3, 1).stream().take(5)
            (1, 3, 9, 27, 81)
        '''
        return stream(self)

class lazyevaluate(Generic[T]):
    '''
        An `Iterable` that delays invocation of `func` until iterated.
        Mainly used as a wrapper for eager evaluated functions, e.g. `sorted`.
    
        >>> lazyevaluate([3, 5, 4, 2, 1], sorted).stream().to(list)
        [1, 2, 3, 4, 5]
    '''

    class _iterator(Generic[T]):
        '''
            The underlying `Iterator` for `lazyevaluate`.
        '''

        def __init__(self, iterable: Iterable[T], func: Callable[[Iterable[T]], Iterable[U]]):
            self.__iterable = iterable
            self.__func = func
            self.__initial = True

        def __iter__(self) -> Iterator[U]:
            return self
        
        def __next__(self) -> U:
            if self.__initial:
                self.__iterable = iter(self.__func(self.__iterable))
                self.__initial = False
            return next(self.__iterable)

    def __init__(self, iterable: Iterable[T], func: Callable[[Iterable[T]], Iterable[U]]):
        '''
            Construct an `Iterable` that delays invocation of `func` until iterated.

            >>> lazyevaluate([3, 5, 4, 2, 1], sorted).stream().to(list)
            [1, 2, 3, 4, 5]
        '''
        self.__iterable = iterable
        self.__func = func
    
    def __iter__(self) -> Iterator[T]:
        '''
            Wrapper of `self.iter()` for usage in language constructs.
        '''
        return self.iter()

    def iter(self) -> Iterator[T]:
        '''
            Obtain an `Iterator` for usage in language constructs.
        '''
        return self._iterator(self.__iterable, self.__func)

    def stream(self) -> stream[T]:
        '''
            Construct an non-reentrant `stream` backed by this `iterate`. Equivalent to `stream(self)`.

            >>> lazyevaluate([3, 5, 4, 2, 1], sorted).stream().to(list)
            [1, 2, 3, 4, 5]
        '''
        return stream(self)

