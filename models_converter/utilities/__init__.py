def remove_prefix(string: str, prefix: str):
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def remove_suffix(string: str, suffix: str):
    if string.endswith(suffix):
        return string[: len(string) - len(suffix)]
    return string
