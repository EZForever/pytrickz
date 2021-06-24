# pytrickz

*A library aimed for providing handy hacks for your daily coding task.*

## What is this

Some syntactic sugar taken from various languages' designs added to Python3 for some coding ease. They are anti-Pythonic and even "Java (or C#) flavored", but they are intuitive (at least to me) and gets the job done.

```python
>>> from pytrickz import *
>>> from pytrickz.extensions import *
>>> 
>>> # Chaining iterable operations
>>> stream.of(1, 2, 3).map(lambda x: x ** 2).to(list)
[1, 4, 9]
>>> 
>>> # Regexp-enabled string operations
>>> 'Albert Einstein'.rematch(r'(\w+) (\w+)').group(2)
'Einstein'
>>> 
>>> # Looped XOR. Everyone's favorite bit operation.
>>> b'abcdef' ^ 0x50
b'123456'
>>> 
```

## Installation & usage

Install directly from GitHub:

```
$ pip3 install -U git+https://github.com/EZForever/pytrickz
```

If you need things in the `pybrickz.extensions` package, [`forbiddenfruit`][forbiddenfruit] need to be installed. Note that `forbiddenfruit` only supports CPython.

Start using right away with `from pytrickz import *`. All features are documented via docstrings so use `help()` if you need guidance.

## Feature highlights

For full feature list, try `help(pytrickz)`. That might help.

### `stream`

Idea ~~stolen~~ borrowed from [`Stream<T>` class in Java 8+][stream-api], allows chaining operations on an iterable and have them lazy-evalulated.

```python
>>> from pytrickz import stream
>>> 
>>> # Currently `stream` support ~30 common operations. `help(stream)` for more.
>>> 
>>> # Crunching numbers
>>> # Newlines are completely optional, added only for readability
>>> stream.of(1, 1, 4, 5, 1, 4) \
...     .unique() \
...     .map(lambda x: x ** 2) \
...     .filter(lambda x: x % 2) \
...     .sum()
... 
26
>>> 
>>> # Hexadecimal countdown because why not
>>> stream.range(15, 0) \
...     .map('0123456789abcdef'.__getitem__) \
...     .to(list)
... 
['f', 'e', 'd', 'c', 'b', 'a', '9', '8', '7', '6', '5', '4', '3', '2', '1']
>>> 
>>> # Transposing a 4x4 "matrix"
>>> my_mat = '048c159d26ae37bf'
>>> stream(my_mat) \
...     .group(4) \
...     .zip() \
...     .flatten() \
...     .join()
... 
'0123456789abcdef'
>>> 
>>> # Even basic I/O with CSV files
>>> stream.fromcsv('example.csv', *(float, None, None, float, float)) \
...     .starmap(lambda mean, mn, mx: (mean, mx - mn)) \
...     .enumerate() \
...     .starmap(lambda idx, data: (idx + 1, *data)) \
...     .tocsv('out.csv', *('gen', 'frames_mean', 'frames_range'))
... 
>>> 
```

### `@extension`

A concept [from C#][extension-methods]. Prepend your method definition with `@extension` and your method appears in every instance of the target class.

```python
>>> from pytrickz import extension
>>> 
>>> # This example needs `forbiddenfruit` to work, since it extends built-in types. `help(extension)` for more info.
>>> 
>>> @extension
... def my_reversed(self: str) -> str: # Type annotation on `self` is necessary, similar to writing `this String` in C#
...     return self[ : : -1]
... 
>>> '123456'.my_reversed()
'654321'
>>> 
>>> # Properties work too
>>> @extension
... @property
... def length(self: str) -> int:
...     return len(self)
... 
>>> '123456'.length
6
```

### Handy extensions for built-in types

Using `@extension` we can extend built-in types to provide even more handy stuff.

```python
>>> from pytrickz.extension import *
>>> 
>>> # The above statement enables all extensions. `help(pytrickz.extension)` for all available modules.
>>> 
>>> # Regexp-enabled string operations
>>> 'Albert Einstein'.rematch(r'(\w+) (\w+)').group(2)
'Einstein'
>>> '1.jpg 2.png'.refindall(r'\.\w{2}g') # Use .refind() if only need the first match
[<re.Match object; span=(1, 5), match='.jpg'>, <re.Match object; span=(7, 11), match='.png'>]
>>> '1.jpg 2.png'.rereplace(r'\.\w{2}g', '.gif')
'1.gif 2.gif'
>>> 
>>> # Hex & Base64 encoding
>>> '313233343536'.unhex() # Also .b64decode()
b'123456'
>>> b'123456'.b64encode() # Also .hex()
'MTIzNDU2'
>>> 
>>> # Checksum calculation
>>> b'123456'.cksum() # CRC-32; name from GNU coreutils
'0972d361'
>>> b'123456'.md5sum() # Also .sha1sum() and .sha256sum()
'e10adc3949ba59abbe56e057f20f883e'
>>> 
>>> # Looped XOR on bytes
>>> b'ABCDEFGH' ^ b'123456'
b'ppppppvz'
>>> b'abcdef' ^ 0x50
b'123456'
>>> 
>>> # Comparsion & arithmetic operators for ctypes integers
>>> # NOTE: Not stable and not feature complete
>>> from ctypes import *
>>> a, b = c_int(1), c_int(2)
>>> a < b
True
>>> a + 1 == b
True
>>> 
```

[forbiddenfruit]: https://pypi.org/project/forbiddenfruit/
[stream-api]: https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html
[extension-methods]: https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods

