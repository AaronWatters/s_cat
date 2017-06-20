
from . import test_data_source
from .. import file_source
import tempfile

class TestFileSource(test_data_source.TestByteSource):
    def get_source(self, byte_data, writeable=False):
        f = self.file
        f.write(byte_data)
        return file_source.FileSource(f, writeable=writeable)

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        # should autodelete
        f = self.file
        if f and not f.closed:
            f.close()
