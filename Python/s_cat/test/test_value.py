# This Python file uses the following encoding: utf-8

import unittest
from .. import value
from .. import key

class TestValues(unittest.TestCase):

    def test_misc(self):
        dummy = value.ValuesContainer()
        dummy = value.Deleted()
        href = b"http://example.com/index.html"
        dummy = value.Reference(href)
        self.assertEqual(dummy.reference_bytes, href)
        dummy = value.Values()
        seq = [b"1", b"12", b"123"]
        for x in seq:
            dummy.add_bytes(x)
        self.assertEqual(dummy.sequence, seq)
        with self.assertRaises(key.FormatError):
            dummy = value.value_from_bytes("XXX")
        with self.assertRaises(key.FormatError):
            dummy = value.values_from_bytes("XXX")

    def test_parse_delete(self):
        encoded = b"012D 5678"
        (values, end) = value.values_from_bytes(encoded, 3)
        self.assertIsInstance(values, value.Deleted)
        self.assertEqual(end, 5)

    def test_delete_roundtrip(self):
        v = value.Deleted()
        bytes = v.to_bytes()
        (v2, end) = value.values_from_bytes(bytes)
        self.assertEqual(end, len(bytes))
        self.assertIsInstance(v2, value.Deleted)
    
    def test_parse_reference(self):
        encoded = b"012R1 A 890"
        (values, end) = value.values_from_bytes(encoded, 3)
        self.assertIsInstance(values, value.Reference)
        self.assertEqual(end, 8)
        self.assertEqual(values.reference_bytes, b"A")
    
    def test_reference_roundtrip(self):
        href = b"http://example.com/index.html"
        v = value.Reference(href)
        bytes = v.to_bytes()
        (v2, end) = value.values_from_bytes(bytes)
        self.assertEqual(end, len(bytes))
        self.assertIsInstance(v2, value.Reference)
        self.assertEqual(v2.reference_bytes, href)

    def test_parse_values(self):
        encoded = b"012V1 A V1 B X"
        (values, end) = value.values_from_bytes(encoded, 3)
        self.assertIsInstance(values, value.Values)
        self.assertEqual(encoded[end:end+1], b"X")
        self.assertEqual(values.sequence, [b"A", b"B"])

    def test_values_roundtrip(self):
        href = b"http://example.com/index.html"
        other = b"example value"
        seq = [href, other]
        v = value.Values(seq)
        bytes = v.to_bytes()
        (v2, end) = value.values_from_bytes(bytes)
        self.assertEqual(end, len(bytes))
        self.assertIsInstance(v2, value.Values)
        self.assertEqual(v2.sequence, seq)
