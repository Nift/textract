"""This module includes a bunch of convenient base classes that are
reused in many of the other parser modules.
"""

import subprocess
import tempfile
import os

import chardet
from .. import exceptions


class BaseParser(object):
    """The :class:`.BaseParser` abstracts out some common functionality
    that is used across all document Parsers. In particular, it has
    the responsibility of handling all unicode and byte-encoding.
    """

    def extract(self, filename, **kwargs):
        """This method must be overwritten by child classes to extract raw
        text from a filename. This method can return either a
        byte-encoded string or unicode.
        """
        raise NotImplementedError('must be overwritten by child classes')

    def encode(self, text, encoding):
        """Encode the ``text`` in ``encoding`` byte-encoding. This ignores
        code points that can't be encoded in byte-strings.
        """
        return text.encode(encoding, 'ignore')

    def process(self, filename, encoding, **kwargs):
        """Process ``filename`` and encode byte-string with ``encoding``. This
        method is called by :func:`textextractor.extractors.process` and wraps
        the :meth:`.BaseParser.extract` method in `a delicious unicode
        sandwich <http://nedbatchelder.com/text/unipain.html>`_.

        """
        # make a "unicode sandwich" to handle dealing with unknown
        # input byte strings and converting them to a predictable
        # output encoding
        # http://nedbatchelder.com/text/unipain/unipain.html#35
        byte_string = self.extract(filename, **kwargs)
        unicode_string = self.decode(byte_string)
        return self.encode(unicode_string, encoding)

    def decode(self, text):
        """Decode ``text`` using the `chardet
        <https://github.com/chardet/chardet>`_ package.
        """
        # only decode byte strings into unicode if it hasn't already
        # been done by a subclass
        if isinstance(text, str):
            return text

        # empty text? nothing to decode
        if not text:
            return u''

        # use chardet to automatically detect the encoding text
        max_confidence, max_encoding = 0.0, None
        result = chardet.detect(text)
        return text.decode(result['encoding'])


class ShellParser(BaseParser):
    """The :class:`.ShellParser` extends the :class:`.BaseParser` to make
    it easy to run external programs from the command line with
    `Fabric <http://www.fabfile.org/>`_-like behavior.
    """

    def run(self, command):
        """Run ``command`` and return the subsequent ``stdout`` and ``stderr``
        as a tuple. If the command is not successful, this raises a
        :exc:`textextractor.exceptions.ShellError`.
        """

        # run a subprocess and put the stdout and stderr on the pipe object
        pipe = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )

        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise exceptions.ShellError(
                command, pipe.returncode, stdout, stderr,
            )

        return stdout, stderr

    def temp_filename(self):
        """Return a unique tempfile name.
        """
        # TODO: it would be nice to get this to behave more like a
        # context so we can make sure these temporary files are
        # removed, regardless of whether an error occurs or the
        # program is terminated.
        handle, filename = tempfile.mkstemp()
        os.close(handle)
        return filename
