
from . import key

def value_from_bytes(encoded_bytes, start=0, expected_indicator=b"V"):
    "get value from encoded bytes, return (value_bytes, end_index) or (None, None)"
    value_bytes = end = None
    nbytes = len(encoded_bytes)
    indicator = encoded_bytes[start:start + 1]
    if indicator == expected_indicator:
        (length, len_end) = key.white_delimited_int(encoded_bytes, start+1)
        end = len_end + length
        value_bytes = encoded_bytes[len_end:end]
        # also consume the white delimiter if available
        if end < nbytes:
            key.assert_is_white(encoded_bytes, end)
            end = end + 1
    else:
        raise key.FormatError("unknown value indicator " + repr(indicator))
    return (value_bytes, end)

class ValuesContainer(object):
    "Abstract superclass for values collection."
    pass

class Deleted(ValuesContainer):
    "Deletion marker."
    
    def to_bytes(self):
        return b"D"

class Reference(ValuesContainer):
    "Reference to external mapping."

    def __init__(self, reference_bytes):
        self.reference_bytes = reference_bytes

    def to_bytes(self):
        byt = self.reference_bytes
        length = len(byt)
        blength = key.unicode_(length).encode("utf8")
        result = b"R" + blength + b"\n" + byt
        return result

class Values(ValuesContainer):
    "Zero or more values as bytes sequences."

    def __init__(self, sequence=()):
        self.sequence = list(sequence)

    def add_bytes(self, bytes):
        self.sequence.append(bytes)

    def to_bytes(self):
        L = []
        for bytes in self.sequence:
            length = len(bytes)
            blength = key.unicode_(length).encode("utf8")
            insert = b"".join([b"V", blength, b"\n", bytes])
            L.append(insert)
        return b"\n".join(L)

def values_from_bytes(encoded_bytes, start=0):
    values = end = None
    nbytes = len(encoded_bytes)
    indicator = encoded_bytes[start:start + 1]
    if indicator == b"D":
        values = Deleted()
        end = start + 1
        # also consume the white delimiter if available
        if end < nbytes:
            key.assert_is_white(encoded_bytes, end)
            end = end + 1
    elif indicator == b"R":
        (bytes, end) = value_from_bytes(encoded_bytes, start, expected_indicator=b"R")
        values = Reference(bytes)
    elif indicator == b"V":
        values = Values()
        while indicator == b"V":
            (bytes, end) = value_from_bytes(encoded_bytes, start)
            values.add_bytes(bytes)
            start = end
            indicator = encoded_bytes[start: start+1]
    else:
        raise key.FormatError("unknown values indicator " + repr(indicator))
    return (values, end)
