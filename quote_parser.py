"""Pulls an optional trailing attribution ("... — Hazrat Ali (r.a.)") off a
raw message so the card can render body text and author separately."""

_DASHES = ("—", "–", "-")  # em dash, en dash, hyphen
MAX_AUTHOR_LEN = 60


def parse_quote(raw: str):
    text = raw.strip()

    for dash in _DASHES:
        sep = f" {dash} "
        if sep in text:
            body, _, tail = text.rpartition(sep)
            body, tail = body.strip(), tail.strip()
            # a bare hyphen is ambiguous ("... - juda yaxshi edi" is a pause,
            # not an attribution) - only trust it when the tail looks like a
            # name/attribution (capitalised), unlike the unambiguous dashes.
            looks_like_name = dash != "-" or tail[:1].isupper()
            if body and 0 < len(tail) <= MAX_AUTHOR_LEN and "\n" not in tail and looks_like_name:
                return body, tail

    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) > 1:
        last = lines[-1].strip()
        if last[:1] in _DASHES and len(last) <= MAX_AUTHOR_LEN:
            author = last.lstrip("".join(_DASHES)).strip()
            if author:
                return "\n".join(lines[:-1]).strip(), author

    return text, None
