

# py3 hack
try:
    unicode_ = unicode
except NameError:
    unicode_ = str


class Key(object):

    "Abstract superclass: an index key."

    def less_than(self, other):
        "compare self to other of same kind."
        raise NotImplementedError("Implement at subclass")

    def to_bytes(self):
        "compare self to other of same kind."
        raise NotImplementedError("Implement at subclass")

    def __lt__(self, other):
        class_test = class_cmp(type(self), type(other))
        if class_test < 0:
            return True
        if class_test > 0:
            return False
        return self.less_than(other)

    def value(self):
        return None

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self.value()) + ")"


class NumberKey(Key):

    "An index key containing a number."

    def __init__(self, number):
        self.number = number

    def less_than(self, other):
        return self.number < other.number

    def value(self):
        return self.number

    def to_bytes(self):
        return b"N" + unicode_(self.number).encode("ascii")


class StringKey(Key):

    "An index key containing a string."

    def __init__(self, string):
        ts = type(string)
        if ts is bytes:
            string = unicode_(string, "utf8")
            ts = type(string)
        assert ts is unicode_
        self.string = string

    def less_than(self, other):
        return self.string < other.string

    def value(self):
        return self.string

    def to_bytes(self):
        byt = self.string.encode("utf8")
        length = len(byt)
        blength = unicode_(length).encode("ascii")
        return b"S" + blength + b"\n" + byt


class CompositeKey(Key):

    "An index key containing a two component keys (list cons)."
    def __init__(self, key1, key2):
        assert isinstance(key1, Key)
        assert isinstance(key2, Key)
        self.key1 = key1
        self.key2 = key2

    def less_than(self, other):
        if self.key1 < other.key1:
            return True
        if other.key1 < self.key1:
            return False
        return (self.key2 < other.key2)

    def value(self):
        return (self.key1.value(), self.key2.value())

    def to_bytes(self):
        byt1 = self.key1.to_bytes()
        byt2 = self.key2.to_bytes()
        return b"\n".join([b"C", byt1, byt2])

class_order = [NumberKey, StringKey, CompositeKey]

def class_cmp(class1, class2):
    index1 = class_order.index(class1)
    index2 = class_order.index(class2)
    return index1 - index2

def from_bytes(encoded_bytes):
    "Decode a key from a byte sequence."
    assert len(encoded_bytes) > 2

