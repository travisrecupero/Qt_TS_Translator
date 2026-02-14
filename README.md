# Qt TS Translator

## Overview

A general-purpose tool that automates translation of Qt Linguist `.ts` files using online translation APIs. Point it at any directory of `.ts` files and it will produce translated output files ready for use in your Qt application.

## Application Statement

Qt applications create translation files (`.ts` files) in XML format, later converted to binary (`.qm` files). These files enable Qt to incorporate translations where needed. Traditionally, translators use Qt Linguist software to manually insert translations, often employed by companies unless they have in-house translators.

## Purpose

This tool automates translations by leveraging multiple online translation APIs. It aims to produce finalized `.ts` files for any Qt application.

## Usage

### Prerequisites

1. Ensure you have Python 3.8 or higher installed.

2. Install dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

### Basic Usage

Translate all `.ts` files in the default directories:

```bash
python main.py
```

### Custom Input/Output Directories

Point the tool at your own `.ts` files:

```bash
python main.py --input /path/to/your/ts/files --output /path/to/output
```

### Project-Specific Config

If your project has technical terms, product codes, or abbreviations that should not be translated (or should be expanded before translation), create a JSON config file:

```json
{
    "ignore_strings": ["USB", "API", "SDK", "HDMI"],
    "transliterate_strings": {
        "Hex": "Hexadecimal",
        "Hi": "High",
        "Lo": "Low"
    }
}
```

Then pass it with `--config`:

```bash
python main.py --config my_project_config.json
```

### All CLI Options

```
python main.py --help

  --input   Input directory containing .ts files (default: ./translations/unfinished/)
  --output  Output directory for translated .ts files (default: ./translations/finished/)
  --config  Path to JSON config file with ignore_strings and transliterate_strings
```

### Language Detection

The tool automatically detects the target language for each `.ts` file by:

1. Reading the `language` attribute from the `<TS>` XML tag (e.g., `<TS version="2.1" language="fr_FR">`)
2. Falling back to the filename pattern (e.g., `app_fr.ts`, `myproject_de_DE.ts`)

Files whose language cannot be determined are skipped with a warning.

### Azure Translator (Optional)

By default, all languages are translated using Google Translate (via deep-translator). If you have a Microsoft Azure Translator API key, the tool will automatically use it for Chinese and Spanish translations for better quality. Create a `secrets.py` file:

```python
subscription_key = "your-azure-subscription-key"
```

This is entirely optional. Without it, Google Translate is used for all languages.

### Qt Commands

In Qt, follow these commands:

1. Generate `.ts` files from your `.ui` files (if not using existing `.ts` files):

    `lupdate Application.pro -ts myapp_fr.ts myapp_es.ts`

2. Generate `.qm` files from the translated `.ts` files:

    `lrelease myapp_fr.ts myapp_es.ts`

## Developer Notes

- The tool uses nidhaloff/deep-translator API, which has a 5k character limit per API call. The number of sublists is calculated dynamically based on content size.
- Due to API calls, the program has a slow runtime. It adds a delay (`sleep(1)`) between string translations and (`sleep(random.uniform(7, 10))`) between each sublist.
- Sample `.ts` files are in `./translations/unfinished`. After execution, finished `.ts` files appear in `./translations/finished`, with translations in lines initially tagged as `<translation type="unfinished"></translation>`.
- In cases of timeout or unavailable translations, English defaults are used.
- Use `constants.py` or a `--config` JSON file to ignore or transliterate certain strings before translation.
- Refer to the API documentation for details on the translation API.
