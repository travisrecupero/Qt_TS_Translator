# CLAUDE.md

## Project Overview

Qt_TS_Translator is a general-purpose Python tool that automates translation of Qt Linguist `.ts` files using Google Translate (via `deep-translator`). It reads untranslated `.ts` files from a configurable input directory, translates all `<source>` strings, and writes completed `.ts` files to a configurable output directory.

## Repository Structure

```
Qt_TS_Translator/
├── main.py                  # Core application logic (entry point, CLI)
├── constants.py             # Default configuration: paths, empty ignore/transliterate dicts
├── requirements.txt         # Python dependency (deep-translator)
├── .gitignore
├── README.md
├── CLAUDE.md
└── translations/
    ├── unfinished/          # Default input: .ts files with <translation type="unfinished">
    │   └── *.ts             # Sample files included
    └── finished/            # Default output: .ts files with completed translations
        └── *.ts
```

## Setup and Running

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt
python main.py
```

**Sole dependency:** `deep-translator==1.11.4` (which pulls in `requests` and `beautifulsoup4`).

**CLI arguments:**
- `--input DIR` — Input directory containing `.ts` files (default: `./translations/unfinished/`)
- `--output DIR` — Output directory for translated files (default: `./translations/finished/`)
- `--config FILE` — Optional JSON config file for project-specific ignore/transliterate strings

## Architecture

The application is procedural, organized into a single module (`main.py`) with a supporting config module (`constants.py`).

### Execution Flow (in `main()`)

1. Parse CLI arguments (`--input`, `--output`, `--config`)
2. Load optional JSON config file into `constants.IGNORE_STRINGS` / `constants.TRANSLITERATE_STRINGS`
3. Discover all `.ts` files in the input directory
4. For each file:
   a. Detect the target language from the `<TS language="...">` XML attribute, falling back to filename pattern
   b. Map the Qt locale code to a translator language code (e.g., `fr_FR` -> `fr`, `zh_CN` -> `zh-CN`)
   c. Extract all source strings from `<source>` XML tags via regex
   d. Identify line numbers of `<translation>` tags in the file
   e. Translate each string with rate-limiting delays
   f. Write a new `.ts` file, replacing `<translation type="unfinished">` lines with translated content

### Key Functions in `main.py`

| Function | Purpose |
|---|---|
| `detect_language()` | Parses `<TS language="...">` from XML, falls back to filename pattern |
| `map_language_code()` | Converts Qt locale (`fr_FR`) to translator code (`fr`); handles Chinese variants |
| `load_config()` | Loads project-specific ignore/transliterate strings from a JSON config file |
| `extract_original_texts()` | Extracts strings between `<source></source>` tags using regex |
| `translate_strings()` | Translates a list of strings via GoogleTranslator with rate limiting and progress output |
| `count_trans_line_numbers()` | Finds line numbers of `<translation>` elements for output writing |
| `create_new_text()` | Writes translated `.ts` file by replacing translation lines |
| `ignore()` | Checks if a string contains terms that should not be translated |
| `transliterate()` | Expands abbreviations before translation using configured mappings |

### Language Detection

The tool detects the target language in two ways:
1. **XML attribute** (preferred): Reads `language="fr_FR"` from the `<TS>` tag
2. **Filename fallback**: Extracts from patterns like `app_fr.ts` or `myapp_de_DE.ts`

The Qt locale code is then mapped to a translator code (e.g., `fr_FR` -> `fr`, `zh_CN` -> `zh-CN`). The legacy `ch` abbreviation is also handled for backward compatibility.

### Configuration (`constants.py`)

- `IGNORE_STRINGS` — Dictionary of terms to skip translation (empty by default; populate via `--config` or directly)
- `TRANSLITERATE_STRINGS` — Abbreviation-to-full-word mappings applied before translation (empty by default)
- `ORIGINAL_TS_PATH` / `NEW_TS_PATH` — Default input/output directory paths

### Config File Format (`--config`)

```json
{
    "ignore_strings": ["USB", "API", "SDK"],
    "transliterate_strings": {"Hex": "Hexadecimal", "Lo": "Low"}
}
```

## Code Conventions

- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Variables:** `snake_case` (some legacy `camelCase` exists, e.g., `matchObject`)
- **File parsing:** Regex-based extraction rather than XML parser for source/translation tags
- **Error handling:** Broad `except Exception` blocks that silently fall back to the original English string
- **No type hints** — functions use inline comments and docstrings selectively
- **No formal logging** — uses `print()` statements for progress output

## Rate Limiting

The tool throttles API calls to avoid being blocked:
- `sleep(random.uniform(0.5, 1.5))` between individual string translations
- Progress printed every 50 strings

## Testing

There is no test suite. The project has no unit tests, test framework, or CI/CD pipeline. Verification is done manually by running `python main.py` and inspecting output files.

## Important Caveats

- The sample `.ts` files in `translations/` are from a specific project; the tool itself works with any Qt `.ts` files
- Full runs on large files are slow due to intentional rate limiting
- Translation quality depends entirely on Google Translate
- `deep-translator` uses Google Translate's unofficial mobile endpoint (no API key needed), but this could break if Google changes it
- Individual strings over ~5000 characters will fail (UI strings are typically well under this)
