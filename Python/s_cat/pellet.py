
from . import key
from . import value

OFFSET_INDICATOR = b'O'

class Pellet(object):

    def __init__(self, pkey, pvalues):
        assert isinstance(pkey, key.Key)
        assert isinstance(pvalues, value.ValuesContainer)
        self.key = pkey
        self.values = pvalues
        self.offset_seek = None
        self.skips_offsets_and_counts = []
        self.payload_length = None

    def set_offsets(self, payload_length, offsets):
        self.payload_length = payload_length
        # validate list content
        self.skips_offsets_and_counts = []
        for (offset, count) in offsets:
            self.skips_offsets_and_counts.append((offset, count))

    def to_bytes(self):
        key_bytes = self.key.to_bytes()
        values_bytes = self.values.to_bytes()
        payload = b"\n".join([key_bytes, values_bytes])
        lpayload = len(payload)
        offsets_list = [key.unicode_(lpayload)]
        for (offset, count) in self.skips_offsets_and_counts:
            pair = key.unicode_(offset) + u":" + key.unicode_(count)
            offsets_list.append(pair)
        offsets = u"-".join(offsets_list)
        offsets_bytes = b"O" + offsets.encode("utf8")
        return b"\n".join([payload, offsets_bytes])

def pellet_from_bytes(encoded_bytes, start=0, with_offsets=True):
    nbytes = len(encoded_bytes)
    (pkey, key_end) = key.key_from_bytes(encoded_bytes, start)
    (pvalues, values_end) = value.values_from_bytes(encoded_bytes, key_end)
    result = Pellet(pkey, pvalues)
    if not with_offsets:
        end = values_end
    else:
        (payload_length, offsets, end) = offsets_from_bytes(encoded_bytes, values_end)
        result.set_offsets(payload_length, offsets)
        # also consume the white delimiter if available
        #if end < nbytes:
        #    print "remainder", repr(encoded_bytes[end:])
        #    key.assert_is_white(encoded_bytes, end)
        #    end = end + 1
    return (result, end)

def offsets_from_bytes(encoded_bytes, start=0, max_length=4048):
    indicator = encoded_bytes[start: start+1]
    if indicator != OFFSET_INDICATOR:
        raise key.FormatError("unknown key indicator " + repr(indicator))
    (offsets_str, end) = key.white_delimited(encoded_bytes, start+1, max_length=max_length)
    if offsets_str is None:
        raise key.FormatError("Could not find end of offsets within limit.")
    offsets = []
    if ("-" in offsets_str):
        # parse offsets
        payload_end = offsets_str.index('-')
        pairs_str = offsets_str[payload_end+1:]
        pairs_str_list = pairs_str.split('-')
        for pair_str in pairs_str_list:
            [offset_str, count_str] = pair_str.split(":")
            offset = int(offset_str)
            count = int(count_str)
            offsets.append((offset, count))
    else:
        # no offsets
        payload_end = end
    payload_length = int(offsets_str[:payload_end])
    return (payload_length, offsets, end)
