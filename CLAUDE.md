# CLAUDE.md

## Project Overview

Qt_TS_Translator is a Python tool that automates translation of Qt Linguist `.ts` files using online translation APIs (Google Translate via `deep-translator` and Microsoft Azure Translator). It reads untranslated `.ts` files from `translations/unfinished/`, translates all `<source>` strings, and writes completed `.ts` files to `translations/finished/`.

## Repository Structure

```
Qt_TS_Translator/
├── main.py                  # Core application logic (entry point)
├── constants.py             # Configuration: ignore lists, transliteration maps, paths
├── requirements.txt         # Python dependencies (pinned versions)
├── secrets.py               # Azure API key (gitignored, must be created manually)
├── .gitignore
├── README.md
└── translations/
    ├── unfinished/          # Input: .ts files with <translation type="unfinished">
    │   ├── t1_ch.ts         # Chinese, German, Spanish, French, Hindi,
    │   ├── t1_de.ts         # Italian, Japanese, Korean, Turkish
    │   └── ...
    └── finished/            # Output: .ts files with completed translations
        ├── t1_ch.ts
        └── ...
```

## Setup and Running

**Requirements:** Python 3.8+

```bash
pip install -r requirements.txt
python main.py
```

**Dependencies:** numpy, requests, lxml, deep-translator (see `requirements.txt` for pinned versions).

**Azure API key:** Chinese and Spanish translations use Microsoft Azure Translator. Create `secrets.py` with:
```python
subscription_key = "your-azure-key-here"
```
This file is gitignored. Without it, the import on line 3 of `main.py` will fail.

## Architecture

The application is procedural, organized into a single module (`main.py`) with a supporting config module (`constants.py`).

### Execution Flow (in `main()`)

1. Discover all `.ts` files in `translations/unfinished/`
2. For each file, extract the language code from the filename (e.g., `t1_fr.ts` -> `fr`)
3. Extract all source strings from `<source>` XML tags via regex
4. Identify line numbers of `<translation>` tags in the file
5. Split strings into 64 sublists (to respect API character limits)
6. Translate each sublist with rate-limiting delays between calls
7. Flatten translated sublists back into a single list
8. Write a new `.ts` file, replacing `<translation type="unfinished">` lines with translated content

### Key Functions in `main.py`

| Function | Purpose |
|---|---|
| `extract_original_texts()` | Extracts strings between `<source></source>` tags using regex |
| `translate_list()` | Core translation dispatcher; applies ignore/transliterate, routes to correct API |
| `count_trans_line_numbers()` | Finds line numbers of `<translation>` elements for output writing |
| `create_new_text()` | Writes translated `.ts` file by replacing translation lines |
| `create_sublists()` | Divides string list into N chunks for API limits |
| `ignore()` | Checks if a string contains terms that should not be translated |
| `transliterate()` | Expands abbreviations (e.g., "Hex" -> "Hexadecimal") before translation |
| `str_to_chinese()` | Calls Microsoft Azure API for English->Chinese translation |
| `str_to_spanish()` | Calls Microsoft Azure API for English->Spanish translation |
| `flatten()` | Merges list of lists into a single list |

### Translation Routing

- **Chinese (`ch`)** and **Spanish (`es`)**: Use Microsoft Azure Translator API (`str_to_chinese`, `str_to_spanish`)
- **All other languages** (de, fr, hi, it, ja, ko, tr): Use Google Translate via `deep-translator`

### Configuration (`constants.py`)

- `NUM_OF_SUBLISTS = 64` — Number of chunks for API call batching
- `IGNORE_STRINGS` — Dictionary of technical terms/model numbers to skip translation
- `TRANSLITERATE_STRINGS` — Abbreviation-to-full-word mappings applied before translation
- `ORIGINAL_TS_PATH` / `NEW_TS_PATH` — Input/output directory paths

## Code Conventions

- **Functions:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Variables:** `snake_case` (some legacy `camelCase` exists, e.g., `originalTexts`, `matchObject`, `retList`)
- **File parsing:** Regex-based extraction rather than XML parser for source/translation tags
- **Error handling:** Broad `except Exception` blocks that silently fall back to the original English string
- **No type hints or docstrings** — functions use inline comments instead
- **No formal logging** — uses `print()` statements for progress output

## Rate Limiting

The tool intentionally throttles API calls to avoid being blocked:
- `sleep(1)` between individual string translations
- `sleep(random.uniform(7, 10))` between sublists
- User agent rotation via `get_random_user_agent()`

## Testing

There is no test suite. The project has no unit tests, test framework, or CI/CD pipeline. Verification is done manually by running `python main.py` and inspecting output files.

## Important Caveats

- The `secrets.py` file must exist with a valid `subscription_key` for the program to import successfully, even if only translating non-Chinese/non-Spanish languages
- The `.ts` files are large (~330-360 KB each, ~8,600 lines) — full runs are slow due to rate limiting
- Translation quality depends entirely on the external APIs
- The `get_proxies()` function exists but is not called anywhere in the main workflow
- The `language` variable is mutated inside `translate_list()` (line 75: `language = 'zh-CN'`), which can cause side effects across loop iterations
