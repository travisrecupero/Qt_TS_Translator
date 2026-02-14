# Maximum characters per sublist (deep-translator API limit is ~5000)
MAX_CHARS_PER_SUBLIST = 4500

# Strings that should not be translated (e.g., product codes, technical terms).
# Add project-specific terms here directly, or load from a JSON config file via --config.
# Format: {'TERM': 'TERM', ...}
IGNORE_STRINGS = {}

# Abbreviations to expand before translation.
# Add project-specific mappings here directly, or load from a JSON config file via --config.
# Format: {'abbreviation': 'full word', ...}
TRANSLITERATE_STRINGS = {}

ORIGINAL_TS_PATH = './translations/unfinished/'
NEW_TS_PATH = './translations/finished/'
