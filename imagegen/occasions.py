"""Maps a detected icon/occasion to the editorial layout's content: which
palette, eyebrow label, optional punchy headline and 3-word tagline fit."""
from .editorial import PALETTES

# icon_key -> (palette_key, eyebrow, headline, tagline)
_OCCASIONS = {
    "cake": ("blush", "TUG'ILGAN KUN TABRIGI", "Tabriklaymiz!", "baxt · sog'lik · omad"),
    "gift": ("blush", "TABRIK", "Muborak bo'lsin!", "quvonch · nur · baxt"),
    "confetti_star": ("blush", "BAYRAM TABRIGI", "Muborak bo'lsin!", "quvonch · nur · baxt"),
    "crescent_star": ("teal_gold", "DINIY HIKMAT", None, "iymon · sabr · najot"),
    "heart": ("blush", "SEVGI IZHORI", None, "sadoqat · mehr · issiqlik"),
    "knot": ("charcoal_gold", "VAFO VA AHD", None, "sodiqlik · or-nomus · so'z"),
    "book": ("charcoal_gold", "HIKMAT SO'ZI", None, "aql · bilim · fazilat"),
    "hourglass": ("charcoal_gold", "HIKMAT SO'ZI", None, "sabr · vaqt · fazilat"),
    "tree": ("sage", "HAYOT VA TABIAT", None, "o'sish · umid · kelajak"),
    "mountain_flag": ("charcoal_gold", "G'ALABA SARI", None, "kuch · maqsad · matonat"),
    "sun": ("lavender", "YORUG' KUN", None, "umid · baxt · quvonch"),
}

_DEFAULT = ("lavender", "IQTIBOS", None, None)


def resolve(icon_key):
    """Returns (palette_dict, eyebrow, headline, tagline) for the given icon
    key (or the generic fallback when icon_key is None/unmatched)."""
    palette_key, eyebrow, headline, tagline = _OCCASIONS.get(icon_key, _DEFAULT)
    return PALETTES[palette_key], eyebrow, headline, tagline
