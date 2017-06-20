import unittest
from .. import data_source

class TestByteSource(unittest.TestCase):

    

    def test_empty(self):
        empty = data_source.BytesSource(b"")
        none_bytes = empty.get_bytes(0, 1, strict=True)
        self.assertIsNone(none_bytes)
        (no_bytes, at_eof) = empty.get_bytes(0, 0, strict=True)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        (no_bytes, at_eof) = empty.get_bytes(0, 100, strict=False)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        with self.assertRaises(IndexError):
            empty.get_bytes(1, 1, strict=False)
        self.assertIsNone(empty.get_bytes_from_ws_to_eof())
        self.assertEquals(empty.get_bytes_to_ws_or_eof(0), b"")
        with self.assertRaises(data_source.ReadOnlyError):
            empty.append(b"abc")
    
    def test_append(self):
        s = data_source.BytesSource(b"", writeable=True)
        none_bytes = s.get_bytes(0, 1, strict=True)
        self.assertIsNone(none_bytes)
        s.append(b"1")
        (one_byte, eof) = s.get_bytes(0, 1, strict=True)
        self.assertEqual(one_byte, b"1")
        self.assertTrue(eof)

    def test_space(self):
        space = data_source.BytesSource(b" ")
        one_bytes = space.get_bytes(0, 1, strict=True)
        self.assertEqual(one_bytes, (b' ', True))
        (no_bytes, at_eof) = space.get_bytes(1, 0, strict=True)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        (no_bytes, at_eof) = space.get_bytes(1, 100, strict=False)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        with self.assertRaises(IndexError):
            space.get_bytes(2, 1, strict=False)
        (no_bytes, start_seek) = space.get_bytes_from_ws_to_eof()
        self.assertEqual(no_bytes, b"")
        self.assertEqual(start_seek, 1)
        no_bytes = space.get_bytes_to_ws_or_eof(0)
        self.assertEqual(no_bytes, b"")

    def test_saasb(self):
        space = data_source.BytesSource(b" aa b")
        two_bytes = space.get_bytes(2, 2, strict=True)
        self.assertEqual(two_bytes, (b'a ', False))
        (no_bytes, at_eof) = space.get_bytes(5, 0, strict=True)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        (no_bytes, at_eof) = space.get_bytes(5, 100, strict=False)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        with self.assertRaises(IndexError):
            space.get_bytes(6, 1, strict=False)
        (some_bytes, start_seek) = space.get_bytes_from_ws_to_eof()
        self.assertEqual(some_bytes, b"b")
        self.assertEqual(start_seek, 4)
        some_bytes = space.get_bytes_to_ws_or_eof(1)
        self.assertEqual(some_bytes, b"aa")
        some_bytes = space.get_bytes_to_ws_or_eof(4)
        self.assertEqual(some_bytes, b"b")

    def test_larger(self):
        prefix = (b"a" * 99) + b" "
        suffix = (b"x" * 123)
        text = (prefix * 3) + suffix
        space = data_source.BytesSource(text)
        two_bytes = space.get_bytes(298, 3, strict=True)
        self.assertEqual(two_bytes, (b'a x', False))
        (no_bytes, at_eof) = space.get_bytes(len(text), 0, strict=True)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        (no_bytes, at_eof) = space.get_bytes(len(text), 100, strict=False)
        self.assertEqual(no_bytes, b"")
        self.assertTrue(at_eof)
        with self.assertRaises(IndexError):
            space.get_bytes(len(text) + 1, 1, strict=False)
        (some_bytes, start_seek) = space.get_bytes_from_ws_to_eof()
        self.assertEqual(some_bytes, suffix)
        self.assertEqual(start_seek, 300)
        some_bytes = space.get_bytes_to_ws_or_eof(100)
        self.assertEqual(some_bytes, prefix[:-1])
        some_bytes = space.get_bytes_to_ws_or_eof(98)
        self.assertEqual(some_bytes, b"a")
        some_bytes = space.get_bytes_to_ws_or_eof(422)
        self.assertEqual(some_bytes, b"x")

    def test_max_offset(self):
        text = b"x" * 10000
        space = data_source.BytesSource(text)
        self.assertIsNone(space.get_bytes_from_ws_to_eof(initial_length=1, max_seek=2))
        self.assertIsNone(space.get_bytes_to_ws_or_eof(1, initial_length=1, max_length=2))

class TestDataSource(unittest.TestCase):

    def test_not_implemented(self):
        xxx = data_source.DataSource()
        with self.assertRaises(NotImplementedError):
            xxx.get_bytes(1,1)
        with self.assertRaises(NotImplementedError):
            xxx.length()
        with self.assertRaises(data_source.ReadOnlyError):
            xxx.append(b"xxx")
