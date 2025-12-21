from enum import Enum

def parse_enum_for_row(enum_attr: Enum) -> str:
    """Helper function to parse Enum attributes for row representation.

    Args:
        enum_attr (Enum): The Enum attribute to parse.
    Returns:
        str: The string representation of the Enum value.
    """
    return enum_attr.value