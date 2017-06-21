# This Python file uses the following encoding: utf-8

import unittest
from .. import key

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

class TestStringKey(unittest.TestCase):

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
