from enum import Enum

from cong.statics import log_template


def parse_enum_for_row(enum_attr: Enum) -> str:
    """
    Helper function to parse Enum attributes for row representation.

    Args:
        enum_attr (Enum): The Enum attribute to parse.

    Returns:
        str: The string representation of the Enum value.

    """
    return enum_attr.value


def unofficial_method(func):
    """
    Decorator that logs calls to _fetch methods.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function that logs before calling the original

    """

    def wrapper(*args, **kwargs):
        log_template(func.__qualname__).warning("This method is not officially supported by the API.")
        log_template(func.__qualname__).warning("Responses may be throttled.")
        return func(*args, **kwargs)

    return wrapper
