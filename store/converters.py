from __future__ import annotations


class UnicodeSlugConverter:
    """Django path converter matching Unicode word characters plus hyphens.

    Product and Category SlugField values use allow_unicode=True, so the URL
    layer must accept the same contract. Python's ``\\w`` is Unicode-aware.
    """

    regex = r"[-\w]+"

    def to_python(self, value: str) -> str:
        return value

    def to_url(self, value: str) -> str:
        return str(value)
