"""
Use argparse to handle command-line arguments.
"""

import argparse
import encodings
import os
import pkgutil

import argcomplete

from . import VERSION
from .parsers import DEFAULT_ENCODING


class AddToNamespaceAction(argparse.Action):
    """This adds KEY,VALUE arbitrary pairs to the argparse.Namespace object
    """
    def __call__(self, parser, namespace, values, option_string=None):
        key, val = values.strip().split('=')
        if hasattr(namespace, key):
            parser.error((
                'Duplicate specification of the key "%(key)s" with --option.'
            ) % locals())
        setattr(namespace, key, val)


# This function is necessary to enable autodocumentation of the script
# output
def get_parser():
    """Initialize the parser for the command line interface and bind the
    autocompletion functionality"""

    # initialize the parser
    parser = argparse.ArgumentParser(
        description=(
            'Command line tool for extracting text from any document. '
        ) % locals(),
    )

    # define the command line options here
    parser.add_argument(
        'filename', help='Filename to extract text.',
    ).completer = argcomplete.completers.FilesCompleter
    parser.add_argument(
        '-e', '--encoding', type=str, default=DEFAULT_ENCODING,
        choices=_get_available_encodings(),
        help='Specify the encoding of the output.',
    )
    parser.add_argument(
        '-m', '--method', default='',
        help='Specify a method of extraction for formats that support it',
    )
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default='-',
        help='Output raw text in this file',
    )
    parser.add_argument(
        '-O', '--option', type=str, action=AddToNamespaceAction,
        help=(
            'Add arbitrary options to various extractors of the form '
            'KEYWORD=VALUE. A full list of available KEYWORD options is '
            'available at http://bit.ly/textextractor-options'
        ),
    )
    parser.add_argument(
        '-v', '--version', action='version', version='%(prog)s '+VERSION,
    )

    # enable autocompletion with argcomplete
    argcomplete.autocomplete(parser)

    return parser


def _get_available_encodings():
    """Get a list of the available encodings to make it easy to
    tab-complete the command line interface.

    Inspiration from http://stackoverflow.com/a/3824405/564709
    """
    available_encodings = set(encodings.aliases.aliases.values())
    paths = [os.path.dirname(encodings.__file__)]
    for importer, modname, ispkg in pkgutil.walk_packages(path=paths):
        available_encodings.add(modname)
    available_encodings = list(available_encodings)
    available_encodings.sort()
    return available_encodings
