'''
    Defines extension methods for `bytes`.
'''

import zlib
import base64
import hashlib
from typing import Union

from .. import extension, stream

@extension(target = (bytes, bytearray))
class ex_bytes(bytes):
    def __xor__(self, other: Union[bytes, bytearray, int]) -> bytes:
        '''
            Perform looped XOR on each element.

            >>> b'ABCDEFGH' ^ b'123456'
            b'ppppppvz'
            >>> b'abcdef' ^ 0x50
            b'123456'
        '''
        if isinstance(other, (bytes, bytearray)):
            return stream.of(self, stream(other).repeat()).zip().starmap(lambda x, y: x ^ y).to(bytes)
        elif isinstance(other, int):
            return stream(self).map(lambda x: x ^ other).to(bytes)
        else:
            return NotImplemented
    """
    def __rxor__(self, other: int) -> bytes:
        # Extending `__rxor__()` is not supported by forbiddenfruit right now
        '''
            Perform looped XOR on each element.

            >>> 0x50 ^ b'abcdef'
            b'123456'
        '''
        return self.__xor__(other)
    """
    # `hex()` is provided in Python stdlib 
    #def hex(self) -> str: pass

    def b64encode(self) -> str:
        '''
            Encode bytes using Base64.

            >>> b'123456'.b64encode()
            'MTIzNDU2'
        '''
        return base64.b64encode(self).decode()

    def cksum(self) -> str:
        '''
            Calculate CRC-32 checksum of given bytes.

            >>> b'123456'.cksum()
            '0972d361'
        '''
        return zlib.crc32(self).to_bytes(4, 'big').hex()

    def md5sum(self) -> str:
        '''
            Calculate MD5 checksum of given bytes.

            >>> b'123456'.md5sum()
            'e10adc3949ba59abbe56e057f20f883e'
        '''
        return hashlib.md5(self).hexdigest()

    def sha1sum(self) -> str:
        '''
            Calculate SHA-1 checksum of given bytes.

            >>> b'123456'.sha1sum()
            '7c4a8d09ca3762af61e59520943dc26494f8941b'
        '''
        return hashlib.sha1(self).hexdigest()

    def sha256sum(self) -> str:
        '''
            Calculate SHA-256 checksum of given bytes.

            >>> b'123456'.sha256sum()
            '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92'
        '''
        return hashlib.sha256(self).hexdigest()

