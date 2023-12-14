# QT_TS_Translator

## Overview
This tool was initially developed as a work project but found practical use beyond its original scope. Please note that the code hosted here might not reflect the most recent updates or improvements. The most up-to-date code resides in my organization's GitLab repository.

The current, up-to-date version of this tool has evolved into a command-line interface (CLI) version integrated into our CI/CD pipeline. It runs translations on a schedule, ensuring that our applications are consistently updated with accurate translations. This evolved version addresses prior caveats related to Spanish and Chinese translations, providing a more robust and reliable solution.

If you are seeking the latest version or wish to contribute, please open an issue or reach out for information on the current codebase available within my organization's infrastructure and boundaries.

## Application Statement

Qt applications create translation files (`.ts` files) in XML format, later converted to binary (`.qm` files). These files enable Qt to incorporate translations where needed. Traditionally, translators use Qt Linguist software to manually insert translations, often employed by companies unless they have in-house translators.

## Purpose

This tool automates translations by leveraging multiple online translation APIs. It aims to produce finalized `.ts` files for Qt applications.

## Usage

### Prerequisites

1. Ensure you have Python 3.8 or higher installed.

2. Install dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

### Steps

1. Run the tool:

    ```bash
    python main.py
    ```

This executes the translation process within the project's environment.

### Qt Commands

In Qt, follow these commands:

1. Use the following command (if not using provided `.ts` files):

    `lupdate Appplication.pro -ts t1_fr.ts t1_sp.ts`
    
    This generates .ts files from your .ui files.

2. Generate .qm files from .ts files:

    `lrelease t1_fr.ts t1_sp.ts`

## Developer Notes

- The tool uses nidhaloff/deep-translator API, which has a 5k character limit per API call.
- Due to API calls, the program has a slow runtime. It adds a delay (`sleep(1)`) between string translations and (`sleep(random.uniform(7, 10))`) between each sublist.
- Find sample `.ts` files in `.\translations\unfinished`. After execution, finished `.ts` files will appear in `\translations\finished`, containing translations in lines initially tagged as `<translation type="unfinished"></translation>`.
- In cases of timeout or unavailable translations, English defaults.
- Use constants.py to ignore or transliterate certain strings before translation for better results.
- For Spanish and Chinese translations, the tool uses Microsoft Translator from Azure due to issues with deep_translator API. Store the API key in secrets.py. To use free translations, comment out lines utilizing str_to_spanish(string) and str_to_chinese(string).
  - this may change once issues are resolved in `deep-translator`
- Refer to the API documentation for details on the translation API.