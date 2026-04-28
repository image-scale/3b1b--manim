"""Iterable manipulation utilities."""


def remove_list_redundancies(lst):
    """Remove duplicates while preserving order.

    Keeps elements in the order they first appear.
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def list_update(l1, l2):
    """Combine two lists, adding elements from l2 not already in l1."""
    result = list(l1)
    for item in l2:
        if item not in result:
            result.append(item)
    return result


def list_difference_update(l1, l2):
    """Return l1 with elements from l2 removed."""
    l2_set = set(l2)
    return [item for item in l1 if item not in l2_set]


def adjacent_pairs(items):
    """Generate adjacent pairs, including wrap-around from last to first."""
    if len(items) == 0:
        return
    for i in range(len(items)):
        yield (items[i], items[(i + 1) % len(items)])


def adjacent_n_tuples(items, n):
    """Generate adjacent n-tuples, wrapping around at the end."""
    if len(items) == 0:
        return
    for i in range(len(items)):
        yield tuple(items[(i + j) % len(items)] for j in range(n))


def batch_by_property(items, property_func):
    """Group consecutive items with the same property value.

    Yields (batch, property_value) tuples.
    """
    if not items:
        return

    current_batch = [items[0]]
    current_prop = property_func(items[0])

    for item in items[1:]:
        prop = property_func(item)
        if prop == current_prop:
            current_batch.append(item)
        else:
            yield (current_batch, current_prop)
            current_batch = [item]
            current_prop = prop

    yield (current_batch, current_prop)
