# This Python file uses the following encoding: utf-8

import unittest
from .. import pellet
from .. import value
from .. import key

class TestPelletFromBytes(unittest.TestCase):

    def test_spec(self):
        encoded = b"N1\nV1\nA\nO7"
        (p, length) = pellet.pellet_from_bytes(encoded)
        to_bytes = p.to_bytes()
        self.assertEqual(to_bytes, encoded)
        self.assertEqual(length, len(encoded))
        padded = b"012 " + encoded +b" XYZ"
        (p, length) = pellet.pellet_from_bytes(padded, 4)
        to_bytes = p.to_bytes()
        self.assertEqual(to_bytes, encoded)
        self.assertEqual(length, padded.index(b"X"))

    def test_round_trip(self):
        k = key.StringKey(u"abc")
        values_bytes = [b"abcdef", b"efg"]
        v = value.Values(values_bytes)
        p = pellet.Pellet(k, v)
        offsets = [(111, 1), (222, 2), (444, 4)]
        dummy_length = 0
        p.set_offsets(dummy_length, offsets)
        to_bytes = p.to_bytes()
        padded = b'012 ' + to_bytes + b' XXX'
        (from_bytes, end) = pellet.pellet_from_bytes(padded, 4)
        self.assertEqual(padded.index(b"X"), end)
        self.assertEqual(from_bytes.values.sequence, values_bytes)
        self.assertEqual(from_bytes.key, k)
        self.assertEqual(from_bytes.skips_offsets_and_counts, offsets)

class TestOffsets(unittest.TestCase):

    def test_payload_only(self):
        encoded = b"012O321"
        (length, offsets, end) = pellet.offsets_from_bytes(encoded, 3)
        self.assertEqual(length, 321)
        self.assertEqual([], offsets)
        self.assertEqual(end, len(encoded))
        encoded1 = b"012O3991 more stuff"
        (length, offsets, end) = pellet.offsets_from_bytes(encoded1, 3)
        self.assertEqual(length, 3991)
        self.assertEqual([], offsets)
        self.assertEqual(end, encoded1.index(b'm'))

    def test_payload_offsets(self):
        encoded = b"012O321-221:2-341:3"
        (length, offsets, end) = pellet.offsets_from_bytes(encoded, 3)
        self.assertEqual(length, 321)
        self.assertEqual([(221, 2), (341, 3)], offsets)
        self.assertEqual(end, len(encoded))
        encoded1 = b"012O3991-221:2-341:3 more stuff"
        (length, offsets, end) = pellet.offsets_from_bytes(encoded1, 3)
        self.assertEqual(length, 3991)
        self.assertEqual([(221, 2), (341, 3)], offsets)
        self.assertEqual(end, encoded1.index(b'm'))

    def test_exceptions(self):
        with self.assertRaises(key.FormatError):   
            encoded = b"012X321-221:2-341:3"
            (length, offsets, end) = pellet.offsets_from_bytes(encoded, 3)
        with self.assertRaises(key.FormatError): 
            encoded = b"O" * 10000
            (length, offsets, end) = pellet.offsets_from_bytes(encoded, 3)
