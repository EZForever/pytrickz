'''
    Defines the `stream` class.

    ```
    from pytrickz.stream import stream

    print(stream.range(5).to(tuple)) # (0, 1, 2, 3, 4)
    ```
'''

import csv
import sys
import itertools

from typing import *
from functools import reduce
from collections import OrderedDict
#from collections.abc import Container

from .typevars import *

class stream(Generic[T]):
    '''
        A class representing a lazy-evaluating stream of operations on `Iterable`s.

        ```
        >>> mylist = [1, 2, 3]
        >>> stream(mylist) \\
        ...     .map(lambda x: x ** 2) \\
        ...     .filter(lambda x: x % 2) \\
        ...     .sum()
        10
        ```
    '''

    # --- Private attributes

    def _lazyevaluate(self, func: Callable[[Iterable[T]], Iterable[T]]) -> None:
        '''
            Apply `func` on the stream, evaluated lazily.
            
            Only for internal use.
        '''
        from .iterables import lazyevaluate
        self._iterable = iter(lazyevaluate(self._iterable, func))

    # --- Constructors

    @classmethod
    def of(cls, *values: T) -> 'stream[T]':
        '''
            Construct a reentrant `stream` object from individual values.

            >>> stream.of(1, 2, 3).map(lambda x: x ** 2).to(tuple)
            (1, 4, 9)
        '''
        return cls(values)
    
    @classmethod
    def range(cls, start_or_stop: int, stop: Union[int, None] = ..., step: int = ...) -> 'stream[int]':
        '''
            Construct a reentrant `stream` object from indices of slice `[0 : stop]` or `[start : stop : step]`.

            If `stop` is specified and is `None`, `start_or_stop` is treated as `start`, i.e. `[start : ]`.

            `step` defaults to `-1` if `start > stop`; `1` otherwise.

            >>> stream.range(5).to(tuple)
            (0, 1, 2, 3, 4)
        '''
        if stop is ...:
            stop = start_or_stop
            start = 0
        else:
            if stop is None:
                stop = sys.maxsize
            start = start_or_stop
        if step is ...:
            step = -1 if start > stop else 1
        return cls(range(start, stop, step))

    @classmethod
    def fromcsv(cls, filename: str, *cols: Union[Type, Callable[[str], U], None], skip_header: bool = ..., dialect: Union[str, csv.Dialect, Type[csv.Dialect]] = ..., **fmtparams) -> 'stream[Tuple[Any, ...]]':
        '''
            Construct a non-reentrant `stream` object from data in a CSV file, convert each column to the type given in `cols` (if present).

            Columns after `cols`, as well as columns with type `None`, are ignored.

            If `skip_header` is `True` (defaults to auto-detect via `csv.Sniffer`), the first line is assumed to be headers and is ignored.

            `dialect` (defaults to auto-detect via `csv.Sniffer`) and `fmtparams` are passed to `csv.reader`.

            >>> stream.fromcsv('data.csv').take(3)
            (('0', '2', '3.7'), ('1', '5', '2.1'), ('2', '8', '5.5'))
            >>> stream.fromcsv('data.csv', *(int, None, float)).take(3)
            ((0, 3.7), (1, 2.1), (2, 5.5))
        '''
        def _generate():
            with open(filename, 'r', newline = '') as f:
                real_header, real_dialect = skip_header, dialect
                if skip_header is ... or dialect is ...:
                    sniffer = csv.Sniffer()
                    sample = ''.join(f.readlines(2))
                    f.seek(0)
                    if skip_header is ...:
                        real_header = sniffer.has_header(sample)
                    if dialect is ...:
                        real_dialect = sniffer.sniff(sample)

                reader = csv.reader(f, real_dialect, **fmtparams)
                if real_header:
                    next(reader)
                
                selector = [x is not None for x in cols]
                real_cols = list(itertools.compress(cols, selector))
                for row in reader:
                    if len(real_cols) > 0:
                        real_row = itertools.compress(row, selector)
                        yield tuple(map(lambda x: x[0](x[1]), zip(real_cols, real_row)))
                    else:
                        yield tuple(row)
        return cls(_generate())

    def __init__(self, *iterables: Iterable[T]):
        '''
            Construct a `stream` object from zero, one or more `Iterable`s.

            The new `stream` is reentrant IFF given nothing or exactly one reentrant `stream` or pure `Iterable`.

            >>> stream([1, 2], [3, 4], [5]).to(tuple)
            (1, 2, 3, 4, 5)
        '''
        argc = len(iterables)
        if argc == 0:
            self._iterable = ()
        elif argc == 1:
            self._iterable = iterables[0]
        else:
            self._iterable = itertools.chain(*iterables)

    def __copy__(self) -> 'stream[T]':
        '''
            Wrapper of `self.copy()` for usage in language constructs.

            >>> import copy
            >>> copy.copy(stream.of(1, 2, 3)).to(tuple)
            (1, 2, 3)
        '''
        return self.copy()

    def copy(self) -> 'stream[T]':
        '''
            Construct a `stream` containing the same values and reentrancy as this `stream`.

            For non-reentrant `stream`s, both `stream`s will share the underlying state.

            >>> a = stream.of(1, 2, 3)
            >>> b = a.copy().map(str)
            >>> a.take(), b.take()
            (1, '1')
        '''
        return self.__class__(self._iterable)
    """
    def stream(self) -> 'stream[T]':
        '''
            Wrapper of `self.copy()` for consistency with other `Iterable`s.

            >>> stream.of(1, 2, 3).stream().to(tuple)
            (1, 2, 3)
        '''
        return self.copy()
    """

    # --- Iterator generation

    def __iter__(self) -> Iterator[T]:
        '''
            Wrapper of `self.iter()` for usage in language constructs.

            >>> [x for x in stream.range(3)]
            [0, 1, 2]
        '''
        return self.iter()

    def iter(self) -> Iterator[T]:
        '''
            Obtain an `Iterator` for usage in language constructs.

            For non-reentrant `stream`s, the returned `Iterator` shares the state of this `stream`.

            >>> [x for x in stream.range(3).iter()]
            [0, 1, 2]
        '''
        if self.isreentrant:
            return iter(self._iterable)
        else:
            return self._iterable

    # --- Reentrancy

    @property
    def isreentrant(self) -> bool:
        '''
            Check if the current `stream` is reentrant.

            >>> stream([1, 2, 3]).isreentrant
            True
            >>> stream(map(str, [1, 2, 3])).isreentrant
            False
        '''
        #return isinstance(self._iterable, Container) or isinstance(self._iterable, range)
        if isinstance(self._iterable, self.__class__):
            return self._iterable.isreentrant
        else:
            return not isinstance(self._iterable, Iterator)

    def reentrant(self) -> 'stream[T]':
        '''
            Ensure the current `stream` is reentrant by iterating and caching the stream.

            For reentrant `stream`s, this operation is a no-op.

            >>> s = stream(map(str, [1, 2, 3])) # `map` object is non-reentrant
            >>> s.to(list), s.to(list)
            (['1', '2', '3'], [])
            >>> s = stream(map(str, [1, 2, 3])).reentrant()
            >>> s.to(list), s.to(list)
            (['1', '2', '3'], ['1', '2', '3'])
        '''
        if not self.isreentrant:
            self._iterable = tuple(self._iterable)
        return self

    def nonreentrant(self) -> 'stream[T]':
        '''
            Ensure the current `stream` is non-reentrant.

            For non-reentrant `stream`s, this operation is a no-op.

            >>> s = stream(range(3)) # `range` object is reentrant
            >>> s.take(), s.take()
            (0, 0)
            >>> s = stream(range(3)).nonreentrant()
            >>> s.take(), s.take()
            (0, 1)
        '''
        if self.isreentrant:
            self._iterable = iter(self._iterable)
        return self

    # --- Stateless intermediate operations

    def prepend(self, *iterables: Iterable[T]) -> 'stream[T]':
        '''
            Prepend `Iterable`s to the stream.

            This is an intermediate operation.

            >>> stream([1, 2]).prepend([3, 4]).to(list)
            [3, 4, 1, 2]
        '''
        if len(iterables) > 0:
            self._iterable = itertools.chain(*iterables, self._iterable)
        return self

    def append(self, *iterables: Iterable[T]) -> 'stream[T]':
        '''
            Append `Iterable`s to the stream.

            This is an intermediate operation.

            >>> stream([1, 2]).append([3, 4]).to(list)
            [1, 2, 3, 4]
        '''
        if len(iterables) > 0:
            self._iterable = itertools.chain(self._iterable, *iterables)
        return self

    def map(self, func: Callable[[T], U]) -> 'stream[U]':
        '''
            Apply `func` on each value in the stream.

            This is an intermediate operation.

            >>> stream.of(1, 2, 3).map(lambda x: x ** 2).to(tuple)
            (1, 4, 9)
        '''
        self._iterable = map(func, self._iterable)
        return self

    def starmap(self, func: Callable[..., U]) -> 'stream[U]':
        '''
            Apply `func` on each `Iterable`'s values in the stream.

            This is an intermediate operation.

            >>> stream([(2, 5), (3, 2), (10, 3)]).starmap(pow).to(list)
            [32, 9, 1000]
        '''
        self._iterable = itertools.starmap(func, self._iterable)
        return self

    def filter(self, func: Callable[[T], bool] = ...) -> 'stream[T]':
        '''
            Filter values in the stream with `func` or value truthiness.

            This is an intermediate operation.

            >>> stream.of(1, 2, 3).filter(lambda x: x % 2).to(tuple)
            (1, 3)
        '''
        self._iterable = filter(None if func is ... else func, self._iterable)
        return self

    def enumerate(self) -> 'stream[Tuple[int, T]]':
        '''
            Convert values in the stream to index-value pairs.

            This is an intermediate operation.

            >>> stream('abc').enumerate().to(list)
            [(0, 'a'), (1, 'b'), (2, 'c')]
        '''
        self._iterable = enumerate(self._iterable)
        return self

    def flatten(self) -> 'stream[U]':
        '''
            Concatenate `Iterable`s in the stream.

            This is an intermediate operation.

            >>> stream([('a', 1), ('b', 2), ('c', 3)]).flatten().to(list)
            ['a', 1, 'b', 2, 'c', 3]
        '''
        #self._iterable = itertools.chain(*self._iterable)
        self._lazyevaluate(lambda x: itertools.chain.from_iterable(x))
        return self

    def slice(self, start_or_stop: int, stop: Union[int, None] = ..., step: int = 1) -> 'stream[T]':
        '''
            Filter values in the stream with slice `[0 : stop]` or `[start : stop : step]`.

            If `stop` is specified and is `None`, `start_or_stop` is treated as `start`, i.e. `[start : ]`

            This is an intermediate operation.

            >>> stream.range(10).slice(1, 5, 2).to(list)
            [1, 3]
        '''
        if stop is ...:
            stop = start_or_stop
            start = 0
        else:
            start = start_or_stop
        self._iterable = itertools.islice(self._iterable, start, stop, step)
        return self

    # --- Stateful intermediate operations

    def sort(self, key: Callable[[T], U] = ..., *, reverse: bool = False) -> 'stream[T]':
        '''
            Sort the values in the stream by the (optional) key and order.

            This is a stateful intermediate operation.

            >>> stream.of(3, 4, 1, 5, 2).sort().to(list)
            [1, 2, 3, 4, 5]
        '''
        #self._iterable = sorted(self._iterable, key = None if key is ... else key, reverse = reverse)
        self._lazyevaluate(lambda x: sorted(x, key = None if key is ... else key, reverse = reverse))
        return self

    def unique(self) -> 'stream[T]':
        '''
            Filter the unique values in the stream.

            This is a stateful intermediate operation.

            >>> stream.of(1, 1, 2, 3, 2).unique().to(list)
            [1, 2, 3]
        '''
        #self._iterable = OrderedDict.fromkeys(self._iterable).keys()
        self._lazyevaluate(lambda x: OrderedDict.fromkeys(x).keys())
        return self

    def reverse(self) -> 'stream[T]':
        '''
            Reverse the order of the values in the stream.

            This is a stateful intermediate operation.

            >>> stream.range(5).reverse().to(list)
            [4, 3, 2, 1, 0]
        '''
        if isinstance(self._iterable, Sequence) or isinstance(self._iterable, Reversible):
            self._iterable = reversed(self._iterable)
        else:
            self._lazyevaluate(lambda x: reversed(tuple(x)))
        return self

    def zip(self, *, default: Any = ...) -> 'stream[Tuple[Any, ...]]':
        '''
            Aggregate values from each `Iterable` in the stream, fill missing values with `default` (if present) or remove unmached values.

            This is a stateful intermediate operation.

            >>> stream([('a', 1), ('b', 2), ('c', 3)]).zip().to(list)
            [('a', 'b', 'c'), (1, 2, 3)]
        '''
        if default is ...:
            self._lazyevaluate(lambda x: zip(*x))
        else:
            self._lazyevaluate(lambda x: itertools.zip_longest(*x, fillvalue = default))
        return self

    def group(self, count: int, *, default: T = ...) -> 'stream[Tuple[T, ...]]':
        '''
            Group values in the stream by given count.

            This is a stateful intermediate operation.

            >>> stream.range(10).group(3).to(list)
            [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
            >>> stream.range(10).group(3, default = 0).to(list)
            [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 0, 0)]
        '''
        def _generate(iterable: Iterable[T]):
            iterator = iter(iterable)
            if default is ...:
                return iter(lambda: tuple(itertools.islice(iterator, count)), ())
            else:
                def _generate_inner():
                    while True:
                        value = tuple(itertools.islice(iterator, count))
                        if len(value) < count:
                            yield tuple(itertools.chain(value, itertools.repeat(default, count - len(value))))
                            return
                        else:
                            yield value
                return _generate_inner()
        
        self._lazyevaluate(_generate)
        return self

    def groupby(self, key: Callable[[T], K] = ..., *, sort: bool = True) -> 'stream[Tuple[K, Iterable[T]]]':
        '''
            Group values in the stream by the (optional) key to key-values pairs.

            This is a stateful intermediate operation.

            >>> stream.of(('a', 1), ('a', 2), ('b', 2)) \\
            ...     .groupby(lambda x: x[0]) \\
            ...     .map(lambda x: (x[0], list(x[1]))) \\
            ...     .to(list)
            [('a', [1, 2]), ('b', [2])]
        '''
        if sort:
            self.sort(key)
        self._iterable = itertools.groupby(self._iterable, key = None if key is ... else key)
        return self

    def repeat(self, times: Optional[int] = None) -> 'stream[T]':
        '''
            Repeat the values in the stream for given times or endlessly.

            This is a stateful intermediate operation.

            >>> stream.range(3).repeat(2).to(list)
            [0, 1, 2, 0, 1, 2]
        '''
        if times is None:
            self._iterable = itertools.cycle(self._iterable)
        else:
            #self._iterable = itertools.chain.from_iterable((tuple(self._iterable), ) * times)
            self._lazyevaluate(lambda x: itertools.chain.from_iterable(itertools.repeat(tuple(x), times)))
        return self

    # --- Terminal operations

    def to(self, cls: Union[Type[R], Callable[[Iterable[T]], R]]) -> R:
        '''
            Extract all values from the stream into a container.

            This is a terminal operation.

            >>> stream.range(3).to(tuple)
            (0, 1, 2)
            >>> stream.range(3).map(lambda x: ('k%d' % x, 'v%d' % x)).to(dict)
            {'k0': 'v0', 'k1': 'v1', 'k2': 'v2'}
        '''
        return cls(self._iterable)

    def tocsv(self, filename: str, *cols: Union[str, None], dialect: Union[str, csv.Dialect, Type[csv.Dialect]] = ..., **fmtparams) -> None:
        '''
            Extract all values from the stream into a CSV file, with header given in `cols` (if present).

            Columns after `cols`, as well as columns with header `None`, are ignored.

            `dialect` (if present) and `fmtparams` are passed to `csv.writer`.

            >>> stream.range(10).map(lambda x: (x, float(x), x * 3 - 1)).tocsv('data.csv', *('x', 'float x', 'f x'))
        '''
        with open(filename, 'w', newline = '') as f:
            if dialect is ...:
                writer = csv.writer(f, dialect, **fmtparams)
            else:
                writer = csv.writer(f, **fmtparams)
            
            selector = [x is not None for x in cols]
            real_cols = list(itertools.compress(cols, selector))
            if len(real_cols) > 0:
                real_rows = (itertools.compress(row, selector) for row in self._iterable)
                writer.writerow(real_cols)
            else:
                real_rows = self._iterable
            writer.writerows(real_rows)

    def take(self, count: int = 1, *, default: T = ...) -> Union[T, Tuple[T]]:
        '''
            Obtain a value or a tuple of values from the stream.

            This is a short-circuiting terminal operation.

            >>> stream.of(2, 3, 5, 7).filter(lambda x: x > 3).take()
            5
            >>> stream.of(2, 3, 5, 7).filter(lambda x: x > 3).take(5, default = 0)
            (5, 7, 0, 0, 0)
        '''
        iterator = iter(self)
        if count == 1:
            value = next(iterator) if default is ... else next(iterator, default)
        else:
            if default is not ...:
                iterator = itertools.chain(iterator, itertools.repeat(default))
            value = tuple(itertools.islice(iterator, count))
        return value

    def reduce(self, func: Callable[[R, T], R], initial: R = ...) -> R:
        '''
            Cumulatively apply `func` to `initial` (if present) and all values in the stream.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).reduce(lambda a, b: a + b)
            6
        '''
        if initial is ...:
            return reduce(func, self._iterable)
        else:
            return reduce(func, self._iterable, initial)

    def count(self) -> int:
        '''
            Count the number of values in the stream. Equivalent to `sum(1 for _ in iter(self))`.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).count()
            3
        '''
        return sum(1 for _ in self._iterable)

    def all(self, func: Callable[[T], bool] = ...) -> bool:
        '''
            Return True if all values in the stream are True when evalulated with `func` or value truthiness.

            If the stream is empty, return True.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).all(lambda x: x > 1)
            False
        '''
        return all(self._iterable if func is ... else map(func, self._iterable))
    
    def any(self, func: Callable[[T], bool] = ...) -> bool:
        '''
            Return True if any value in the stream is True when evalulated with `func` or value truthiness.

            If the stream is empty, return False.

            This is a short-circuiting terminal operation.

            >>> stream.of(1, 2, 3).any(lambda x: x > 0)
            True
        '''
        return any(self._iterable if func is ... else map(func, self._iterable))

    def foreach(self, func: Callable[[T], Any]) -> None:
        '''
            Call `func` on each value in the stream.

            This is a terminal operation.

            >>> stream.range(3).foreach(print)
            0
            1
            2
        '''
        for x in self._iterable:
            func(x)

    def sum(self, initial: R = 0) -> R:
        '''
            Returns the sum of `initial` and values in the stream. Equivalent to `sum(self, initial)`.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).sum()
            6
        '''
        return sum(self._iterable, initial)

    def min(self, key: Callable[[T], U] = ..., *, default: T = ...) -> T:
        '''
            Returns the smallest of values in the stream, compared by the optional key function.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).min()
            1
        '''
        try:
            return min(self._iterable, key = None if key is ... else key)
        except ValueError:
            if default is ...:
                raise
            else:
                return default

    def max(self, key: Callable[[T], U] = ..., *, default: T = ...) -> T:
        '''
            Returns the largest of values in the stream, compared by the optional key function.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).max()
            3
        '''
        try:
            return max(self._iterable, key = None if key is ... else key)
        except ValueError:
            if default is ...:
                raise
            else:
                return default

    def join(self, separator: str = '') -> str:
        '''
            Concatenate all values in the stream to form a string, separated by the optional `separator`.

            This is a terminal operation.

            >>> stream.of(1, 2, 3).map(str).join(' ')
            '1 2 3'
        '''
        return separator.join(self._iterable)

