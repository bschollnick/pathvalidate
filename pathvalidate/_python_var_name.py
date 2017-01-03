# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import re

import dataproperty as dp
from mbstrdecoder import MultiByteStrDecoder

from ._common import NameSanitizer
from ._error import (
    InvalidCharError,
    InvalidReservedNameError,
    NullNameError
)


class PythonVarNameSanitizer(NameSanitizer):
    __PYTHON_RESERVED_KEYWORDS = [
        "and", "del", "from", "not", "while",
        "as", "elif", "global", "or", "with",
        "assert", "else", "if", "pass", "yield",
        "break", "except", "import", "print",
        "class", "exec", "in", "raise",
        "continue", "finally", "is", "return",
        "def", "for", "lambda", "try",
    ]
    __PYTHON_BUILTIN_CONSTANTS = [
        "False", "True", "None", "NotImplemented", "Ellipsis", "__debug__",
    ]

    __RE_INVALID_VAR_NAME = re.compile("[^a-zA-Z0-9_]")
    __RE_INVALID_VAR_NAME_HEAD = re.compile("^[^a-zA-Z]+")

    @property
    def reserved_keywords(self):
        return (
            self.__PYTHON_RESERVED_KEYWORDS + self.__PYTHON_BUILTIN_CONSTANTS)

    def validate(self):
        self._validate(self._value)

    def sanitize(self, replacement_text=""):
        sanitize_var_name = self.__RE_INVALID_VAR_NAME.sub(
            replacement_text, self._unicode_str)

        # delete invalid char(s) in the beginning of the variable name
        is_delete_head = any([
            dp.is_empty_string(replacement_text),
            self.__RE_INVALID_VAR_NAME_HEAD.search(
                replacement_text) is not None,
        ])

        if is_delete_head:
            sanitize_var_name = self.__RE_INVALID_VAR_NAME_HEAD.sub(
                "", sanitize_var_name)
        else:
            match = self.__RE_INVALID_VAR_NAME_HEAD.search(sanitize_var_name)
            if match is not None:
                sanitize_var_name = (
                    match.end() * replacement_text +
                    self.__RE_INVALID_VAR_NAME_HEAD.sub("", sanitize_var_name)
                )

        try:
            self._validate(sanitize_var_name)
        except InvalidReservedNameError:
            sanitize_var_name += "_"
        except NullNameError:
            pass

        return sanitize_var_name

    def _validate(self, value):
        self._validate_null_string(value)

        unicode_var_name = MultiByteStrDecoder(value).unicode_str

        if self._is_reserved_keyword(unicode_var_name):
            raise InvalidReservedNameError(
                "{:s} is a reserved keyword by pyhon".format(unicode_var_name))

        match = self.__RE_INVALID_VAR_NAME.search(unicode_var_name)
        if match is not None:
            raise InvalidCharError(
                "invalid char found in the variable name: '{}'".format(
                    re.escape(match.group())))

        match = self.__RE_INVALID_VAR_NAME_HEAD.search(unicode_var_name)
        if match is not None:
            raise InvalidCharError(
                "the first character of the variable name is invalid: '{}'".format(
                    re.escape(match.group())))


def validate_python_var_name(var_name):
    """
    :param str var_name: Name to validate.
    :raises pathvalidate.NullNameError: If the ``var_name`` is empty.
    :raises pathvalidate.InvalidCharError: If the ``var_name`` is invalid as
        `Python identifier
        <https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`__.
    :raises pathvalidate.InvalidReservedNameError:
        If the ``var_name`` is equals to
        `Python reserved keywords
        <https://docs.python.org/3/reference/lexical_analysis.html#keywords>`__
        or
        `Python built-in constants
        <https://docs.python.org/3/library/constants.html>`__.

    :Examples:

        :ref:`example-validate-var-name`
    """

    PythonVarNameSanitizer(var_name).validate()


def sanitize_python_var_name(var_name, replacement_text=""):
    """
    Make a valid Python variable name from ``var_name``.

    To make a valid name:

    - Replace invalid characters for a Python variable name within
      the ``var_name`` with the ``replacement_text``
    - Delete invalid chars for the beginning of the variable name
    - Append under bar (``"_"``) at the tail of the name if sanitized name
      is one of the Python reserved names

    :param str filename: Name to sanitize.
    :param str replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    :raises ValueError: If ``var_name`` or ``replacement_text`` is invalid.

    :Examples:

        :ref:`example-sanitize-var-name`

    .. note::

        Reserved names by Python will not be replaced.

    .. seealso::

        :py:func:`.validate_python_var_name`
    """

    return PythonVarNameSanitizer(var_name).sanitize(replacement_text)