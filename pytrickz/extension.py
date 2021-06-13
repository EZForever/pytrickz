'''
    Defines the `extension` decorator.

    ```
    from pytrickz.extension import extension

    @extension
    def my_reversed(self: str) -> str:
        return self[ : : -1]
    
    print('123456'.my_reversed()) # 654321
    ```
'''

import inspect
import warnings

try:
    import forbiddenfruit
except ImportError:
    forbiddenfruit = None

from typing import *

'''
    Type alias for all types that supports the `@extension` decorator.

    Currently this includes all `Callable`s (includes class methods, static methods and properties), as well as classes.
'''
SupportsExtension = TypeVar('SupportsExtension', Callable, classmethod, staticmethod, property, type)

class ExtensionWarning(Warning):
    '''
        Warning caregory for `extension`-related events.
    '''
    pass

def _get_direct_superclasses(cls: type) -> Tuple[type, ...]:
    '''
        Returns the direct superclasses of a class.

        Only for internal use.
    '''
    hierarchy = inspect.getclasstree(cls.__mro__, unique = True)
    to_search = hierarchy.copy()
    while len(to_search) > 0:
        entries, to_search = to_search, []
        for entry in entries:
            if isinstance(entry, list):
                to_search.extend(entry)
            elif entry[0] == cls:
                return entry[1]
    return ()

def _get_extendable_attributes(cls: type) -> List[Any]:
    '''
        Returns all extendable (`SupportsExtension`) attributes defined in a class.

        Only for internal use.
    '''
    return [v for v in cls.__dict__.values() if isinstance(v, SupportsExtension.__constraints__)]

def extension(func_or_cls: SupportsExtension = ..., *, name: str = ..., target: Union[type, Iterable[type]] = ..., overwrite: bool = False) -> SupportsExtension:
    '''
        Declare a function to be an extension to the target class(es).
        A single target class can be implied by the type annotation of the first argument (`self` or `cls`).

        ```
        @extension
        def my_reversed(self: str) -> str:
            return self[ : : -1]
        
        print('123456'.my_reversed()) # 654321
        ```

        For class methods, static methods and properties, the corresponding decorators must apply before extending, i.e. below `extension`.

        ```
        @extension
        @property
        def length(self: str) -> str:
            return len(self)
        
        print('123456'.length) # 6
        ```

        This decorator can be applied to a class; this way all attributes defined in the class are extended to the target class.
        The target class can be inferred by direct inheritance; `name` is ignored.

        ```
        @extension
        class ex_str(str):
            def reversed(self) -> int:
                return reversed(self)
        
        print('123456'.reversed()) # 654321
        ```
    '''

    if func_or_cls is ...:
        return lambda x: extension(x, name = name, target = target, overwrite = overwrite)
    
    if isinstance(func_or_cls, type):
        cls = func_or_cls

        if target is ...:
            target = _get_direct_superclasses(cls)

        for func in _get_extendable_attributes(cls):
            extension(func, target = target, overwrite = overwrite)

        return cls

    func = func_or_cls

    if isinstance(func, (classmethod, staticmethod)):
        real_func = func.__func__
    elif isinstance(func, property):
        real_func = func.fget or func.fset or func.fdel
    else:
        real_func = func

    if name is ...:
        name = real_func.__name__

    if target is ...:
        if isinstance(func, staticmethod):
            raise TypeError('Cannot infer target class from a static method')
        else:
            arg_specs = inspect.getfullargspec(real_func)
            if len(arg_specs.args) < 1:
                target_resolved = False
            else:
                target = arg_specs.annotations.get(arg_specs.args[0])
                target_resolved = target is not None and isinstance(target, type)
            if not target_resolved:
                raise TypeError(f'Invalid implied target class: {repr(target)}')

    if isinstance(target, type):
        target = (target, )

    for tgt in target:
        if not overwrite and getattr(tgt, name, None) is not None:
            warnings.warn(f'Ignoring extension "{real_func.__qualname__}" for class "{tgt.__qualname__}": target method exists', ExtensionWarning, stacklevel = 2)
            continue

        if tgt.__module__  == 'builtins':
            # Built-in types require forbiddenfruit to operate
            if forbiddenfruit is None:
                raise RuntimeError('Extending built-in types requires forbiddenfruit')
            else:
                forbiddenfruit.curse(tgt, name, func)
        else:
            # Otherwise assigning the value should be enough
            setattr(tgt, name, func)

    return func

