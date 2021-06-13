#!/usr/bin/env python3

from pytrickz import *
from pytrickz.extensions import *

def main():
    print('313233343536'.unhex(), b'123456'.b64encode(), 'MTIzNDU2'.b64decode())
    print(stream.range(3).map(str).isreentrant)
    print(stream.range(3).map(lambda x: (str(x), x)).to(dict))
    print(iterables.iterate(lambda x: x * 3, 1).stream().take(5))
    print(stream.of(1, 2, 2, 3, 4, 5, 4) \
        .unique() \
        .map(lambda x: x ** 2) \
        .filter(lambda x: x % 2) \
        .map(str) \
        .join(', '))
    stream.fromcsv('example.csv', *(float, None, None, float, float)) \
        .starmap(lambda mean, mn, mx: (mean, mx - mn)) \
        .enumerate() \
        .starmap(lambda idx, data: (idx + 1, *data)) \
        .tocsv('out.csv', *('gen', 'frames_mean', 'frames_range'))

if __name__ == '__main__':
    main()

