import re


def split_content_by_regex(
    regex: re.Pattern, content: str, regex_has_match: bool = False
) -> tuple[list[str], list[str]]:
    parts = regex.split(content)

    if regex_has_match:
        return parts[::2], parts[1::2]  # others, matches

    return parts
