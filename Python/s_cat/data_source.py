
import re

ws_re = br"\s"
ws_pattern = re.compile(ws_re)

class ReadOnlyError(IOError):
    "Object is read only: mutation not permitted"
    pass

class DataSource:

    """
    Abstract superclass: Interface to indexed byte resource.
    """

    def get_bytes(self, start_seek, length, strict=True):
        """
        Get length bytes from the resource starting at seek start_seek.
        If strict is False then the returned bytes may be shorter than length
        if the read reaches the end of the file.__base__

        Return (bytes_read, at_eof) on success, else None if too few bytes.

        Raise IndexError if start_seek is past eof.
        """
        raise NotImplementedError("Implement at subclass")

    def length(self):
        """
        Return last index of data source
        """
        raise NotImplementedError("Implement at subclass")

    def append(self, add_bytes):
        """
        Add bytes to end of data and return initial seek position.
        """
        raise ReadOnlyError("Operation not implemented.")

    def get_bytes_from_ws_to_eof(self, initial_length=128, max_seek=1000000):
        """
        Get bytes from last whitespace character to eof.
        return (bytes, start_seek) on success or None on failure.
        """
        buffer_length = self.length()
        seek_offset = initial_length
        while seek_offset < max_seek:
            seek_position = max(0, buffer_length - seek_offset)
            (bytes_read, at_eof) = self.get_bytes(seek_position, seek_offset, strict=False)
            assert at_eof, "read should reach or exceed eof"
            match = None
            for match in ws_pattern.finditer(bytes_read):
                #print repr(bytes_read), "match is", match, match.span()
                pass
            if match is not None:
                start_seek = match.span()[1]
                bytes_match = bytes_read[start_seek:]
                absolute_seek = seek_position + start_seek
                return (bytes_match, absolute_seek)
            if seek_offset > buffer_length:
                return None
            seek_offset += seek_offset
        return None

    def get_bytes_to_ws_or_eof(self, start_seek, initial_length=128, max_length=1000000):
        """
        Read bytes from start seek to just before the first whitespace or the end of file.
        Return bytes between the start_seek and the first whitespace character, or None on failure
        """
        length = initial_length
        while length < max_length:
            (bytes_read, at_eof) = self.get_bytes(start_seek, length, strict=False)
            match = ws_pattern.search(bytes_read)
            if match:
                bytes_before_ws = bytes_read[:match.start()]
                return bytes_before_ws
            if at_eof:
                return bytes_read
            length += length
        return None

class BytesSource(DataSource):

    def __init__(self, byte_data, writeable=False):
        self.byte_data = bytes(byte_data)
        self.writeable = writeable

    def get_bytes(self, start_seek, length, strict=True):
        end_seek = start_seek + length
        byte_data = self.byte_data
        nbytes = len(byte_data)
        if start_seek > nbytes:
            raise IndexError("seek start past end of file.")
        if strict and end_seek > nbytes:
            return None
        at_eof = (end_seek >= len(byte_data))
        return (byte_data[start_seek:end_seek], at_eof)

    def append(self, add_bytes):
        if not self.writeable:
            raise ReadOnlyError("Byte source is not writeable.")
        seek = self.length()
        self.byte_data = self.byte_data + bytes(add_bytes)

    def length(self):
        return len(self.byte_data)
