from deep_translator import GoogleTranslator
from time import sleep
from timeit import default_timer as timer
from datetime import timedelta

import re
import constants
import os
import json
import argparse
import random


def detect_language(filepath):
    """Detect target language from the <TS> tag's language attribute, fall back to filename."""
    with open(filepath) as f:
        for line in f:
            match = re.search(r'<TS[^>]*\slanguage="([^"]+)"', line)
            if match:
                return match.group(1)
            # Stop searching once we're past the header
            if '<context>' in line or '<message>' in line:
                break
    # Fallback: extract from filename (e.g., app_fr.ts, myapp_de_DE.ts, t1_ko.ts)
    basename = os.path.splitext(os.path.basename(filepath))[0]
    match = re.search(r'_([a-z]{2}(?:_[A-Z]{2})?)$', basename)
    if match:
        return match.group(1)
    return None


def map_language_code(qt_locale):
    """Convert Qt locale code (e.g., 'fr_FR', 'zh_CN') to translator language code."""
    if qt_locale is None:
        return None
    # Handle Chinese variants (including legacy 'ch' abbreviation)
    if qt_locale.startswith('zh') or qt_locale.lower() == 'ch':
        if 'TW' in qt_locale or 'Hant' in qt_locale:
            return 'zh-TW'
        return 'zh-CN'
    # For everything else, use first two characters (e.g., fr_FR -> fr, de_DE -> de)
    return qt_locale[:2]


def load_config(config_path):
    """Load project-specific ignore/transliterate strings from a JSON config file."""
    if config_path and os.path.isfile(config_path):
        with open(config_path) as f:
            config = json.load(f)
        if 'ignore_strings' in config:
            for s in config['ignore_strings']:
                constants.IGNORE_STRINGS[s] = s
        if 'transliterate_strings' in config:
            constants.TRANSLITERATE_STRINGS.update(config['transliterate_strings'])
        print("Loaded config from " + config_path)


# gets all strings in between <source></source> tags, returns list
def extract_original_texts(filename, path):
    strings = ''
    with open(path) as ts_file:
        for line in ts_file:
            strings = strings + line
    return re.findall(
        r'(?s)(?<=<source>)(.*?)(?=</source>)', strings, flags=re.S)


# translate a list of strings using Google Translate
def translate_strings(strings, language):
    translator = GoogleTranslator(source='en', target=language)
    translations = []
    total = len(strings)

    for i, string in enumerate(strings):
        sleep(random.uniform(0.5, 1.5))
        string = transliterate(string)
        try:
            if ignore(string):
                translations.append(string)
            else:
                translated = translator.translate(string)
                translations.append(translated)
        except Exception:  # if element cant be translated just use original
            translations.append(string)

        if (i + 1) % 50 == 0 or (i + 1) == total:
            print('  Translated ' + str(i + 1) + '/' + str(total))

    return translations


# returns true if string contains a term in constants.IGNORE_STRINGS
def ignore(string):
    if not constants.IGNORE_STRINGS:
        return False
    for word in string.split(' '):
        if word in constants.IGNORE_STRINGS:
            return True
    return False


# returns transliterated string if string is in constants.TRANSLITERATE_STRINGS
def transliterate(string):
    if not constants.TRANSLITERATE_STRINGS:
        return string
    words = string.split(' ')
    result = []
    for word in words:
        if word in constants.TRANSLITERATE_STRINGS:
            result.append(constants.TRANSLITERATE_STRINGS[word])
        else:
            result.append(word)
    return ' '.join(result)


# returns list of line numbers where <translation></translation> tags are present
def count_trans_line_numbers(filename, path):
    counter = 0
    pos_arr = list()
    with open(path) as ts_file:
        for line in ts_file:
            matchObject = re.search(
                r'(?<=<translation).*(?=</translation>)', line)
            if(matchObject != None):
                pos_arr.append(counter)
            counter = counter + 1
    return pos_arr


# copies old .ts to new file, replacing <translation> lines with translated content
def create_new_text(filename, path, save_path, pos_arr, translations, language):
    i = 0  # line counter for input file
    j = 0  # pos_arr_iterator

    print("Size of position array: " + str(len(pos_arr)))
    print("Size of translation list: " + str(len(translations)))
    with open(path, "r") as input:
        with open(save_path, "w", encoding='utf-8') as output:
            for line in input:
                if(j == len(translations)-1):  # if is last translation / end of translations
                    if "<translation type" in line:
                        trans_str = translations[j]
                        trans_line = "\t\t<translation>" + trans_str + "</translation>\n"
                        output.write(trans_line)
                    else:
                        output.write(line)  # write rest of lines
                else:
                    if(i == pos_arr[j]):  # when i == pos_arr[j] -> translation line
                        trans_str = translations[j]
                        trans_line = "\t\t<translation>" + trans_str + "</translation>\n"
                        output.write(trans_line)
                        j = j + 1
                    else:
                        output.write(line)
                    i = i + 1


def main():
    parser = argparse.ArgumentParser(
        description='Translate Qt .ts files using Google Translate.')
    parser.add_argument('--input', default=constants.ORIGINAL_TS_PATH,
                        help='Input directory containing .ts files (default: %(default)s)')
    parser.add_argument('--output', default=constants.NEW_TS_PATH,
                        help='Output directory for translated .ts files (default: %(default)s)')
    parser.add_argument('--config', default=None,
                        help='Path to JSON config file with ignore_strings and transliterate_strings')
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    # Ensure paths end with separator
    if not input_path.endswith('/'):
        input_path += '/'
    if not output_path.endswith('/'):
        output_path += '/'

    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Load optional project-specific config
    load_config(args.config)

    start = timer()

    file_arr = [f for f in os.listdir(input_path) if f.endswith('.ts')]
    print(file_arr)

    for filename in file_arr:
        original_ts_path = input_path + filename
        new_ts_path = output_path + filename

        # Detect language from XML attribute, fall back to filename
        qt_locale = detect_language(original_ts_path)
        language = map_language_code(qt_locale)

        if language is None:
            print('Could not detect language for ' + filename + ', skipping.')
            continue

        print('Working on ' + filename + ' (' + str(qt_locale) + ' -> ' + language + ')')

        master_list = extract_original_texts(
            filename, original_ts_path)  # every string to be translated

        print("Number of strings to be translated: " + str(len(master_list)))
        # line number of every translation occurence in .ts (starting at 0)
        pos_arr = count_trans_line_numbers(filename, original_ts_path)

        # translate all strings
        translations = translate_strings(master_list, language)

        # insert each translated string into new .ts
        create_new_text(filename, original_ts_path,
                        new_ts_path, pos_arr, translations, language)

        end = timer()
        print("Elapsed Time: " + str(timedelta(seconds=end-start)))
        print(filename + " finished.\n")


if __name__ == "__main__":
    main()
