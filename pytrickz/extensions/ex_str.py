'''
    Defines extension methods for `str`.
'''

import re
import base64
from typing import List, Match, Optional

from .. import extension

@extension
class ex_str(str):
    def unhex(self) -> bytes:
        '''
            Hex decode the string using the given encoding.

            >>> '313233343536'.unhex()
            b'123456'
        '''
        return bytes.fromhex(self)
    
    def b64decode(self) -> bytes:
        '''
            Decode the Base64 encoded string.

            >>> 'MTIzNDU2'.b64decode()
            b'123456'
        '''
        return base64.b64decode(self)

    def rematch(self, pattern: str) -> Optional[Match[str]]:
        '''
            Match the whole string to the given regexp pattern.

            >>> name = 'Albert Einstein'
            >>> 'name' if name.rematch(r'\w+ \w+') else 'not name'
            'name'
            >>> name.rematch(r'(\w+) (\w+)').group(2)
            'Einstein'
        '''
        return re.fullmatch(pattern, self)

    def refind(self, sub: str) -> Optional[Match[str]]:
        '''
            Similar to `find()` but accepts regexps.

            To restrict the match at the beginning of the string, prepend `'^'` to `sub`.

            >>> '1.jpg 2.png'.refind(r'\.\w{2}g')
            <re.Match object; span=(1, 5), match='.jpg'>
            >>> '1.jpg 2.png'.refind('x') is None
            True
        '''
        return re.search(sub, self)

    def refindall(self, sub: str) -> List[Match[str]]:
        '''
            Similar to `find()` but returns all matching substrings and accepts regexps.

            >>> '1.jpg 2.png'.refindall(r'\.\w{2}g')
            [<re.Match object; span=(1, 5), match='.jpg'>, <re.Match object; span=(7, 11), match='.png'>]
            >>> '1.jpg 2.png'.refindall('x')
            []
        '''
        return list(re.finditer(sub, self))

    def rereplace(self, old: str, new: str, count: int = ...) -> str:
        '''
            Similar to `replace()` but accepts regexps.

            >>> '1.jpg 2.png'.rereplace(r'\.\w{2}g', '.gif')
            '1.gif 2.gif'
        '''
        if count is ...:
            return re.sub(old, new, self)
        else:
            return re.sub(old, new, self, count)

