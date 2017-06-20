from . import data_source
import os

class FileSource(data_source.DataSource):

    def __init__(self, open_file, writeable=False):
        self.open_file = open_file
        self.writeable = writeable

    def close(self):
        self.open_file.close()
        self.open_file = None

    def get_bytes(self, start_seek, length, strict=True):
        f = self.open_file
        if f is None:
            raise IOError("No open file.")
        end_seek = self.length()
        if start_seek > end_seek:
            raise IndexError("seek past end of file.")
        if strict and start_seek + length > end_seek:
            return None
        f.seek(start_seek)
        result = f.read(length)
        this_seek = f.tell()
        at_eof = (this_seek >= end_seek)
        return (result, at_eof)

    def append(self, add_bytes):
        self.assertIsWriteable()
        # length seeks to eof
        seek = self.length()
        self.open_file.write(add_bytes)
        return seek

    def length(self):
        f = self.open_file
        f.seek(0, os.SEEK_END)
        end_seek = f.tell()
        return end_seek
