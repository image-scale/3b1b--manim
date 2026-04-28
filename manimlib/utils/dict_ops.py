"""Dictionary operation utilities."""


def merge_dicts_recursively(*dicts):
    """Merge dictionaries recursively.

    Later dictionaries take precedence. If the same key exists in multiple
    dictionaries and both values are dicts, they are merged recursively.
    Otherwise, the later value overwrites the earlier one.
    """
    result = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Both are dicts, merge recursively
                result[key] = merge_dicts_recursively(result[key], value)
            else:
                # Overwrite with the later value
                result[key] = value
    return result
