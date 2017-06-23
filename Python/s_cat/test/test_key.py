# This Python file uses the following encoding: utf-8

import unittest
from .. import key

class TestWhiteDelimited(unittest.TestCase):

    def test_basic(self):
        test_bytes = b'012 45 789'
        test012 = key.white_delimited(test_bytes)
        self.assertEqual((u'012', 4), test012)
        test45 = key.white_delimited(test_bytes, 4)
        self.assertEqual((u'45', 7), test45)
        test789 = key.white_delimited(test_bytes, 7)
        self.assertEqual((u'789', 10), test789)
        test_none = key.white_delimited(test_bytes, 10)
        none_none = (None, None)
        self.assertEqual(test_none, none_none)
        too_big = b'x' * 100
        test_none = key.white_delimited(too_big)
        self.assertEqual(test_none, none_none)

class TestWhiteDelimitedInt(unittest.TestCase):

    def test_basic(self):
        test_bytes = b'012 45 789'
        test_bytes2 = b'0.2 45 7.9'
        test012 = key.white_delimited_int(test_bytes)
        self.assertEqual((12, 4), test012)
        with self.assertRaises(ValueError):
            test012 = key.white_delimited_int(test_bytes2)
        test45 = key.white_delimited_int(test_bytes, 4)
        self.assertEqual((45, 7), test45)
        test789 = key.white_delimited_int(test_bytes, 7)
        self.assertEqual((789, 10), test789)
        with self.assertRaises(ValueError):
            test_none = key.white_delimited_int(test_bytes, 10)
        too_big = b'x' * 100
        with self.assertRaises(ValueError):
            test_none = key.white_delimited_int(too_big)

class TestWhiteDelimitedNumber(unittest.TestCase):

    def test_basic(self):
        test_bytes = b'012 45 7.9'
        test_bytes2 = b'012 45 7.x'
        test012 = key.white_delimited_number(test_bytes)
        self.assertEqual((12, 4), test012)
        test45 = key.white_delimited_number(test_bytes, 4)
        self.assertEqual((45, 7), test45)
        test789 = key.white_delimited_number(test_bytes, 7)
        self.assertEqual((7.9, 10), test789)
        with self.assertRaises(ValueError):
            test789 = key.white_delimited_number(test_bytes2, 7)
        with self.assertRaises(ValueError):
            test_none = key.white_delimited_number(test_bytes, 10)
        too_big = b'x' * 100
        with self.assertRaises(ValueError):
            test_none = key.white_delimited_int(too_big)

class TestKeySuperClass(unittest.TestCase):

    def test_not_implemented(self):
        k1 = key.Key()
        rpr = repr(k1)
        self.assertEqual(rpr, "Key(None)")
        k2 = key.Key()
        with self.assertRaises(ValueError):
            lessthan = (k1 < k2)
        with self.assertRaises(NotImplementedError):
            lessthan = k1.less_than(k2)
        with self.assertRaises(NotImplementedError):
            byt = k1.to_bytes()

class TestNumberKey(unittest.TestCase):

    def test_lt(self):
        n1 = key.NumberKey(1)
        self.assertEqual(n1.value(), 1)
        self.assertEqual(n1.to_bytes(), b"N1")
        n2 = key.NumberKey(1 + 1e-10)
        self.assertTrue(n1 < n2)
        self.assertFalse(n2 < n1)
        s1 = key.StringKey("abc")
        self.assertTrue(n1 < s1)
        self.assertFalse(s1 < n1)
        c1 = key.CompositeKey(s1, n2)
        self.assertTrue(n1 < c1)
        self.assertFalse(c1 < n1)
        srt = list(sorted([s1,n1,c1,n2]))
        self.assertEqual([n1, n2, s1, c1], srt)

    def test_eq(self):
        n1 = key.NumberKey(1)
        n1prime = key.NumberKey(1)
        n2 = key.NumberKey(2)
        self.assertTrue(n1 == n1prime)
        self.assertFalse(n1 == n2)

    def test_parse(self):
        n = key.NumberKey(1012)
        to_bytes = n.to_bytes()
        (from_bytes, end) = key.key_from_bytes(to_bytes)
        self.assertEqual(from_bytes.value(), 1012)
        self.assertEqual(end, len(to_bytes))
        padded = b"0123" + to_bytes + b" 56"
        (from_bytes, end) = key.key_from_bytes(padded, 4)
        self.assertEqual(from_bytes.value(), 1012)
        # end index includes white space separator.
        self.assertEqual(end, 4 + len(to_bytes) + 1)
        n_float = key.NumberKey(123e-12)
        to_bytes_float = n_float.to_bytes()
        (from_bytes_float, end_float) = key.key_from_bytes(to_bytes_float)
        self.assertEqual(from_bytes_float.value(), 123e-12)
        self.assertEqual(end_float, len(to_bytes_float))

class TestStringKey(unittest.TestCase):

    def test_parse(self):
        s = key.StringKey("Äijö")
        #s = key.StringKey("abcd")
        to_bytes = s.to_bytes()
        (from_bytes, end) = key.key_from_bytes(to_bytes)
        #self.assertEqual(from_bytes.value(), "abcd"); return
        self.assertEqual(from_bytes.value(), u"Äijö")
        self.assertEqual(end, len(to_bytes))
        padded = b"0123" + to_bytes + b" 56"
        (from_bytes, end) = key.key_from_bytes(padded, 4)
        self.assertEqual(from_bytes.value(), u"Äijö")
        # end index includes white space separator.
        self.assertEqual(end, 4 + len(to_bytes) + 1)
        padded_wrong = b"0123" + to_bytes + b"x56"
        with self.assertRaises(key.FormatError):
            dummy = key.key_from_bytes(padded_wrong, 4)

    def test_lt(self):
        s1 = key.StringKey("abc")
        self.assertEqual(s1.value(), "abc")
        s2 = key.StringKey("abc0")
        self.assertTrue(s1 < s2)
        self.assertFalse(s2 < s1)
        n1 = key.NumberKey(1)
        self.assertTrue(n1 < s1)
        self.assertFalse(s1 < n1)
        c1 = key.CompositeKey(s2, n1)
        self.assertTrue(s1 < c1)
        self.assertFalse(c1 < s1)
        srt = list(sorted([s1,n1,c1,s2]))
        self.assertEqual([n1, s1, s2, c1], srt)

    def test_to_bytes(self):
        s1 = key.StringKey("Äijö")
        byt = s1.to_bytes()
        self.assertEqual(b"S6\n\xc3\x84ij\xc3\xb6", byt)

class TestCompositeKey(unittest.TestCase):

    def test_parse(self):
        s1 = key.StringKey("abc")
        n1 = key.NumberKey(1)
        c1 = key.CompositeKey(s1, n1)
        to_bytes = c1.to_bytes()
        (from_bytes, end) = key.key_from_bytes(to_bytes)
        self.assertEqual(from_bytes.value(), (u"abc", 1))
        self.assertEqual(end, len(to_bytes))
        padded = b"0123" + to_bytes + b" 56"
        (from_bytes, end) = key.key_from_bytes(padded, 4)
        self.assertEqual(from_bytes.value(), ("abc", 1))

    def test_lt(self):
        s1 = key.StringKey("abc")
        n1 = key.NumberKey(1)
        s2 = key.StringKey("abcd")
        n2 = key.NumberKey(10)
        c1 = key.CompositeKey(s1, n1)
        c3 = key.CompositeKey(s2, n2)
        c2 = key.CompositeKey(s1, s2)
        self.assertEqual(c1.value(), ("abc", 1))
        self.assertTrue(c1 < c2)
        self.assertFalse(c2 < c1)
        self.assertTrue(c2 < c3)
        self.assertFalse(c3 < c2)
        self.assertTrue(c1 < c3)
        self.assertFalse(c3 < c1)
        self.assertTrue(n1 < c3)
        self.assertFalse(c3 < n1)
        self.assertTrue(s1 < c3)
        self.assertFalse(c3 < s1)
        srt = list(sorted([c3,c2,n2,s1,n1,c1,s2]))
        self.assertEqual([n1,n2,s1,s2,c1,c2,c3], srt)

    def test_to_bytes(self):
        s1 = key.StringKey("Äijö")
        n2 = key.NumberKey(10)
        c1 = key.CompositeKey(n2, s1)
        byt = c1.to_bytes()
        self.assertEqual(b'C\nN10\nS6\n\xc3\x84ij\xc3\xb6', byt)


class TestFromBytesSpec(unittest.TestCase):

    def test_int(self):
        encoded = b"012 N567 90"
        (from_bytes, end) = key.key_from_bytes(encoded, 4)
        self.assertTrue(isinstance(from_bytes, key.NumberKey))
        self.assertEqual(from_bytes.value(), 567)
        self.assertEqual(end, 9)

    def test_float(self):
        encoded = b"012 N5.7 90"
        (from_bytes, end) = key.key_from_bytes(encoded, 4)
        self.assertTrue(isinstance(from_bytes, key.NumberKey))
        self.assertEqual(from_bytes.value(), 5.7)
        self.assertEqual(end, 9)

    def test_short_string(self):
        encoded = b"012 S1 a 9012"
        (from_bytes, end) = key.key_from_bytes(encoded, 4)
        self.assertTrue(isinstance(from_bytes, key.StringKey))
        self.assertEqual(from_bytes.value(), u"a")
        self.assertEqual(end, 9)

    def test_longer_string(self):
        longer_bytes = b"X" * 100000
        longer = u"X" * 100000
        encoded = b"012 S100000 " + longer_bytes + b" 9012"
        (from_bytes, end) = key.key_from_bytes(encoded, 4)
        self.assertTrue(isinstance(from_bytes, key.StringKey))
        self.assertEqual(from_bytes.value(), longer)
        self.assertEqual(end, 100013)

    def test_short_composite(self):
        encoded = b"0123 C S1 a N5.7 xxx"
        (from_bytes, end) = key.key_from_bytes(encoded, 5)
        self.assertIsInstance(from_bytes, key.CompositeKey)
        self.assertEqual(from_bytes.value(), (u"a", 5.7))
        self.assertEqual(end, 17)

    def test_exceptions(self):
        with self.assertRaises(key.FormatError):
            dummy = key.key_from_bytes("S-4 xxx")
        with self.assertRaises(key.FormatError):
            dummy = key.key_from_bytes("Y3 xxx")

