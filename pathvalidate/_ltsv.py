"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


import re

from ._common import preprocess, validate_null_string
from .error import InvalidCharError


__RE_INVALID_LTSV_LABEL = re.compile("[^0-9A-Za-z_.-]", re.UNICODE)


def validate_ltsv_label(label: str) -> None:
    """
    Verifying whether ``label`` is a valid
    `Labeled Tab-separated Values (LTSV) <http://ltsv.org/>`__ label or not.

    :param label: Label to validate.
    :raises pathvalidate.NullNameError: If the ``label`` is empty.
    :raises pathvalidate.InvalidCharError:
        If invalid character(s) found in the ``label`` for a LTSV format label.
    """

    validate_null_string(label, error_msg="label is empty")

    match_list = __RE_INVALID_LTSV_LABEL.findall(preprocess(label))
    if match_list:
        raise InvalidCharError(
            "invalid character found for a LTSV format label: {}".format(match_list)
        )


def sanitize_ltsv_label(label: str, replacement_text: str = "") -> str:
    """
    Replace all of the symbols in text.

    :param label: Input text.
    :param replacement_text: Replacement text.
    :return: A replacement string.
    :rtype: str
    """

    validate_null_string(label, error_msg="label is empty")

    return __RE_INVALID_LTSV_LABEL.sub(replacement_text, preprocess(label))
