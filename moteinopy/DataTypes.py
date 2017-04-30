def _hexprints(n):
    """
    Returns a hex sting of length 2 that represents the number n
    :raises ValueError if 0 > n or n > 255
    :param n: int
    :return: string
    """

    if isinstance(n, str):
        n = ord(n)
    if 0 > n or n > 255:
        raise ValueError("n(" + str(n) + ") doesn't fit for _hexprints")
    if n > 15:
        return hex(n)[2:]
    else:
        return '0' + hex(n)[2:]


def _hex2dec(s):
    """
    returns the int represented by hex string s

    :param s: string
    :return: int
    """
    if not len(s) == 2:
        raise ValueError("s(" + str(s) + ") did not fit for _hex2dec")
    else:
        return int(s, base=16)


class DataType(object):
    NofBytes = None
    ReturnType = None

    @staticmethod
    def hex(i):
        pass

    def hexprints(self, i=None):
        if i is not None and type(i) is not self.ReturnType:
            raise ValueError("Wrong Datatype, expected " +
                             str(self.ReturnType) + " but got " +
                             str(type(i)))
        else:
            return self.hex(i)


class Byte(DataType):
    """
    A class describing the byte datatype
    """
    NofBytes = 1
    ReturnType = int

    @staticmethod
    def hex(i=None):
        if i is None:
            i = 0
        if i > 2**8:
            raise ValueError("The number given to Byte.hexprints() doesn't fit, it was: " + str(i))
        return _hexprints(i)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s)


class Char(DataType):
    ReturnType = str
    NofBytes = 1

    @staticmethod
    def hex(i=None):
        if i is None:
            i = '0'
        if ord(i) > 2**8:
            raise ValueError("asj")
        return _hexprints(i)

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s)


class UnsignedInt(DataType):
    """
    A class describing the unsigned int datatype
    """
    NofBytes = 2
    ReturnType = int

    @staticmethod
    def hex(i=None):
        if i is None:
            i = 0
        if not 0 <= i < 2**16:
            raise ValueError("The number given to UnsignedInt.hexprints() doesn't fit, it was: " + str(i))
        return _hexprints(i % 256) + _hexprints(int(i/2**8))

    @staticmethod
    def hex2dec(s):
        return _hex2dec(s[2:4])*2**8 + _hex2dec(s[:2])


class Int(DataType):
    NofBytes = 2
    ReturnType = int

    @staticmethod
    def hex(i=None):
        if i is None:
            i = 0
        if not -2**15 <= i <= 2**15-1:
            raise ValueError("The number given to Int.hexprints() doesn't fit, it was: " + str(i))
        if i >= 0:
            return UnsignedInt.hex(i)
        else:
            return UnsignedInt.hex(2**16+i)

    @staticmethod
    def hex2dec(s):
        i = UnsignedInt.hex2dec(s)
        if i > 2**15-1:
            i -= 2**16
        return i


class UnsignedLong(DataType):
    NofBytes = 4
    ReturnType = int

    @staticmethod
    def hex(i=None):
        if i is None:
            i = 0
        Warning("UnsignedLong is untested code")
        if type(i) is not int:
            raise ValueError("UnsingedLong.hexprints expected int but got " + str(type(i)))
        if not 0 <= i < 2**32:
            raise ValueError("unsignedLong.hexprints expected an int in the range of 0-2^32 but got " + str(i))
        return (_hexprints(i % 256) + _hexprints((i >> 8) % 256) +
                _hexprints((i >> 16) % 256) + _hexprints(i >> 24))

    @staticmethod
    def hex2dec(s):
        Warning("UnsignedLong is untested code")
        if len(s) != 8:
            raise ValueError("UnsignedLong.hex2dec expected string of length 8 but received: " + s)
        return ((_hex2dec(s[6:8]) << 24) + (_hex2dec(s[4:6]) << 16) +
                (_hex2dec(s[2:4]) << 8) + (_hex2dec(s[:2])))


class Long(DataType):
    NofBytes = 4
    ReturnType = int

    @staticmethod
    def hex(i=None):
        if i is None:
            i = 0
        Warning("Long is untested code")
        if type(i) is not int:
            raise ValueError("Long.hexprints expected int but got " + str(type(i)))
        if not -2**31 < i < 2**31:
            raise ValueError("Long.hexprints expected an int in the range of -2^31-2^31 but got " + str(i))
        if i >= 0:
            return UnsignedLong.hex(i)
        else:
            return UnsignedLong.hex(i + 2**32)

    @staticmethod
    def hex2dec(s):
        Warning("Long is untested code")
        if len(s) != 8:
            raise ValueError("Long.hex2dec expected string of length 8 but received: " + s)
        i = UnsignedLong.hex2dec(s)
        if i > 2**31:
            return i - 2**32
        else:
            return i


class Bool(DataType):
    NofBytes = 1
    ReturnType = bool

    @staticmethod
    def hex(i=None):
        if i is None:
            i = False
        if type(i) is not bool:
            raise ValueError('unexpected arguement in Bool.hexprint, expected bool but got ' + str(type(i)))
        if i:
            return "01"
        else:
            return "00"

    @staticmethod
    def hex2dec(s):
        if not len(s) == 2:
            raise ValueError('Bool.hex2dec expected string of length 2 but got: ' + s)
        if s == b"00":
            return False
        else:
            return True


class Array(DataType):
    """
    A class to describe the array datatype, requires the subtype to be defined
    """

    def __init__(self, subtype, n):
        if not issubclass(subtype.__class__, DataType):
            raise ValueError("problem in Array.__init__(), subtype is not a Datatype!")
        self.SubType = subtype
        if type(subtype) is Char:
            self.ReturnType = str
        else:
            self.ReturnType = list
        self.N = n
        self.NofBytes = subtype.NofBytes*n

    def hexprints(self, l=None):

        if self.ReturnType is str:
            returner = str()
            if not l:
                l = str()
            while len(l) < self.N:
                l += " "
            for L in l:
                returner += self.SubType.hexprints(L)
            return returner
        else:
            returner = str()
            if not l:
                l = list()
            while len(l) < self.N:
                l.append(0)
            for L in l:
                returner += self.SubType.hexprints(L)
            return returner

    def hex2dec(self, s):
        returner = list()
        for i in range(self.N):
            returner.append(self.SubType.hex2dec(s[:self.SubType.NofBytes*2]))
            s = s[self.SubType.NofBytes*2:]
        if type(self.SubType) is Char:
            return_str = str()
            for i in returner:
                return_str += chr(i)
            return return_str
        else:
            return returner

# a dictionary of known datatypes to more easily call them
types = {
    'byte': Byte(),
    'char': Char(),
    'unsigned int': UnsignedInt(),
    'int': Int(),
    'bool': Bool(),
    'unsigned long': UnsignedLong(),
    'long': Long(),
}
