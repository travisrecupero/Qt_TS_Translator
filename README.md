# Qt TS Translator

## Overview

A general-purpose tool that automates translation of Qt Linguist `.ts` files using online translation APIs. Point it at any directory of `.ts` files and it will produce translated output files ready for use in your Qt application.

## Application Statement

Qt applications create translation files (`.ts` files) in XML format, later converted to binary (`.qm` files). These files enable Qt to incorporate translations where needed. Traditionally, translators use Qt Linguist software to manually insert translations, often employed by companies unless they have in-house translators.

## Purpose

This tool automates translations using Google Translate (via [deep-translator](https://github.com/nidhaloff/deep-translator)). It aims to produce finalized `.ts` files for any Qt application.

## Usage

### Dev Container (Recommended)

The project includes a dev container with Python, deep-translator, and Qt linguist tools (`lupdate`, `lrelease`, `lconvert`) pre-installed.

**VS Code:** Open the project and select "Reopen in Container" when prompted (requires the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension).

**Docker CLI:**

```bash
docker build -t qt-ts-translator -f .devcontainer/Dockerfile .
docker run -it -v $(pwd):/workspace qt-ts-translator bash
```

Inside the container you have the full workflow available:

```bash
# Generate .ts files from your Qt project
lupdate Application.pro -ts myapp_fr.ts myapp_es.ts

# Translate .ts files
python main.py --input /path/to/ts/files --output /path/to/output

# Generate .qm binary files
lrelease myapp_fr.ts myapp_es.ts
```

### Local Setup

If you prefer to run without Docker:

1. Ensure you have Python 3.8 or higher installed.

2. Install dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

3. Optionally install Qt linguist tools for `lupdate`/`lrelease`:

    ```bash
    # Debian/Ubuntu
    sudo apt install qt6-l10n-tools
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

## Developer Notes

- The tool uses [nidhaloff/deep-translator](https://github.com/nidhaloff/deep-translator) which has a ~5k character limit per individual string. UI strings are typically well under this limit.
- Due to API calls, the program has a slow runtime. It adds a random delay (`sleep(0.5-1.5s)`) between string translations to avoid rate limiting.
- Sample `.ts` files are in `./translations/unfinished`. After execution, finished `.ts` files appear in `./translations/finished`, with translations in lines initially tagged as `<translation type="unfinished"></translation>`.
- In cases of timeout or unavailable translations, English defaults are used.
- Use `constants.py` or a `--config` JSON file to ignore or transliterate certain strings before translation.
- Refer to the API documentation for details on the translation API.
