from sortedcontainers import SortedDict

keys = SortedDict()


def press_key(key) -> None:
    keys[key] = True


def release_key(key) -> None:
    if key in keys:
        keys[key] = False


def is_pressed(key) -> bool:
    if key in keys:
        return keys.get(key)
    return False
