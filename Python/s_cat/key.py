
from . import data_source

# py3 hack
try:   # pragma: no cover
    unicode_ = unicode
except NameError:
    unicode_ = str


class FormatError(ValueError):
    "Byte sequence is not recognized."
    pass


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
        blength = unicode_(length).encode("utf8")
        result = b"S" + blength + b"\n" + byt
        return result


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

def key_from_bytes(encoded_bytes, start=0):
    "Decode a key from a byte sequence prefix. Return (key, end_index)."
    key = end = None
    nbytes = len(encoded_bytes)
    assert nbytes >= start + 2
    indicator = encoded_bytes[start:start + 1]
    if indicator == b"N":
        # parse a number
        (number, end) = white_delimited_number(encoded_bytes, start+1)
        key = NumberKey(number)
    elif indicator == b"S":
        # parse a string
        (length, len_end) = white_delimited_int(encoded_bytes, start+1)
        end = len_end + length
        if (length < 0) or (end > nbytes):
            raise FormatError("invalid length " + repr((length, len_end, nbytes)))
        chunk = encoded_bytes[len_end:end]
        #print "chunk", map(ord, chunk)
        uni_str = unicode_(chunk, "utf8")
        #print "string out", uni_str
        key = StringKey(uni_str)
        # also consume the white delimiter if available
        if end < nbytes:
            assert_is_white(encoded_bytes, end)
            end = end + 1
    elif indicator == b"C":
        # parse a composite
        assert_is_white(encoded_bytes, start+1)
        (key1, end1) = key_from_bytes(encoded_bytes, start+2)
        (key2, end) = key_from_bytes(encoded_bytes, end1)
        key = CompositeKey(key1, key2)
    else:
        raise FormatError("unknown key indicator " + repr(indicator))
    return (key, end)

def assert_is_white(encoded_bytes, index):
    match = data_source.ws_pattern.match(encoded_bytes, index)
    if match is None:
        raise FormatError("Expected whitepace not found.")

def white_delimited_int(encoded_bytes, start=0, max_length=20):
    (chunk, end) = white_delimited(encoded_bytes, start, max_length=20)
    if chunk is None:
        raise FormatError("white delimited chunk not found")
    return (int(chunk), end)

def white_delimited_number(encoded_bytes, start=0, max_length=20):
    (chunk, end) = white_delimited(encoded_bytes, start, max_length=20)
    if chunk is None:
        raise FormatError("white delimited chunk not found")
    try:
        return (int(chunk), end)
    except ValueError:
        return (float(chunk), end)

def white_delimited(encoded_bytes, start=0, max_length=20):
    "find utf8 segment of bytes from start to first whitespace or end of bytes or None"
    white_match = data_source.ws_pattern.search(encoded_bytes, start, start + max_length)
    segment = end = None
    if white_match is not None:
        ws_index = white_match.start()
        segment = encoded_bytes[start: ws_index]
        end = ws_index + 1
    else:
        b_len = len(encoded_bytes)
        if (start < b_len) and (b_len - start) <= max_length:
            segment = encoded_bytes[start:]
            end = b_len
    if segment is not None:
        segment = unicode_(segment, "utf8")
    return (segment, end)
