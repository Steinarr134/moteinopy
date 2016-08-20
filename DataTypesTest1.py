from moteinopy.DataTypes import *
from random import randint as r


def test(type, h, l, repeats):
    for _ in range(repeats):
        i = r(h, l)
        s = type.hexprints(i)
        v = type.hex2dec(s)
        if i != v:
            print(str(type) + " i: " + str(i) + " s: " + str(s) + " v: " + str(v))


test(Byte(), 0, 255, 50)
test(Int(), -30000, 32000, 50)
test(UnsignedInt(), 0, 60000, 50)
test(Long(), -2**31, 2**31, 50)
test(UnsignedLong(), 0, 2**32, 50)

char = Char()
for _ in range(50):
    i = r(0, 255)
    s = char.hexprints(chr(i))
    v = char.hex2dec(s)
    assert i == v
