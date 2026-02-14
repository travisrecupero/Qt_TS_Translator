from deep_translator import GoogleTranslator
from lxml.html import fromstring
from time import sleep
from numpy import random
from timeit import default_timer as timer
from datetime import timedelta

import re
import constants
import os
import requests
import uuid
import json
import argparse

# Azure subscription key - loaded from secrets.py if available
subscription_key = None
try:
    from secrets import subscription_key
except ImportError:
    pass


# returns a random user agent to hide our actual browser information
def get_random_user_agent():
    user_agents = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
                   "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36",
                   "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
                   "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
                   "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
                   "Mozilla/5.0 (compatible; MSIE 6.0; Windows NT 5.1)",
                   "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:31.0) Gecko/20100101 Firefox/31.0",
                   "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
                   "Opera/9.80 (Windows NT 6.2; Win64; x64) Presto/2.12.388 Version/12.17",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
                   "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"]
    return user_agents[random.randint(0, len(user_agents) - 1)]


# returns a set of proxies that have Google and https capability
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]') and i.xpath('.//td[6][contains(text(),"yes")]'):
            # Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0],
                             i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


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
    originalTexts = list()
    strings = ''

    with open(path) as ts_file:
        for line in ts_file:
            strings = strings + line

    strings = re.findall(
        r'(?s)(?<=<source>)(.*?)(?=</source>)', strings, flags=re.S)
    originalTexts = strings
    return originalTexts


# using Google Translate and optionally Microsoft Azure, return list
def translate_list(sub_list, language):
    retList = list()
    sleep(random.uniform(7, 10))
    for string in sub_list:
        sleep(1)
        string = transliterate(string)
        try:
            if ignore(string):
                retList.append(string)
            elif subscription_key and language in ('zh-CN', 'zh-TW'):
                azure_lang = 'zh-Hans' if language == 'zh-CN' else 'zh-Hant'
                translated = str_to_azure(string, azure_lang)
                retList.append(translated)
            elif subscription_key and language == 'es':
                translated = str_to_azure(string, 'es')
                retList.append(translated)
            else:
                translated = GoogleTranslator(
                    'en', language).translate(string)
                retList.append(translated)
        except Exception:  # if element cant be translated just use original
            retList.append(string)
    return retList


# returns true if string contains a term in constants.IGNORE_STRINGS
def ignore(string):
    if not constants.IGNORE_STRINGS:
        return False
    string = string.split(' ')
    for substr in string:
        if substr in constants.IGNORE_STRINGS:
            return True
    return False


# returns transliterated string if string is in constants.TRANSLITERATE_STRINGS
def transliterate(string):
    if not constants.TRANSLITERATE_STRINGS:
        return string
    string = string.split(' ')
    ret_val = []

    for substr in string:
        if substr in constants.TRANSLITERATE_STRINGS:
            ret_val.append(constants.TRANSLITERATE_STRINGS[substr])
        else:
            ret_val.append(substr)

    ret_val = ' '.join(ret_val)
    return ret_val


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


# copies old .ts to new file (except on line where  <translation></translation> tags are present), adds new translations
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


# divide list into n sublists while maintaining order, n = number of sublists
def create_sublists(list, n):
    sublists = []
    len_l = len(list)
    for i in range(n):
        start = int(i*len_l/n)
        end = int((i+1)*len_l/n)
        sublists.append(list[start:end])
    return sublists


# turns any list of lists into one contiguous list
def flatten(list_of_lists):
    flat_list = [item for sublist in list_of_lists for item in sublist]
    return flat_list


def calculate_num_sublists(strings, max_chars_per_sublist):
    """Calculate number of sublists needed based on total character count and API limits."""
    total_chars = sum(len(s) for s in strings)
    if total_chars == 0:
        return 1
    # Ceiling division to ensure each sublist stays under the character limit
    return max(1, -(-total_chars // max_chars_per_sublist))


# returns given english string translated via Microsoft Azure Translator API
def str_to_azure(string, target_lang):
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "eastus2"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': target_lang
    }

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': str(string)
    }]

    request = requests.post(
        constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    # Grab translated string
    text = response[0]['translations'][0]['text']

    return str(text)


def main():
    parser = argparse.ArgumentParser(
        description='Translate Qt .ts files using online translation APIs.')
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

    if subscription_key:
        print("Azure Translator API key found. Using Azure for Chinese and Spanish.")
    else:
        print("No Azure API key found. Using Google Translate for all languages.")

    start = timer()
    file_arr = []

    for file in os.listdir(input_path):
        if file.endswith('.ts'):
            file_arr.append(file)
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

        # Calculate number of sublists based on content size and API character limits
        num_sublists = calculate_num_sublists(
            master_list, constants.MAX_CHARS_PER_SUBLIST)
        sublists = create_sublists(master_list, num_sublists)
        print("Splitting into " + str(num_sublists) + " sublists (avg size: " +
              str(len(sublists[0]) if sublists else 0) + ")")

        # translate each sublist
        i = 0
        for sublist in sublists:
            # translate each sublist
            sublist = translate_list(sublist, language)
            sublists[i] = sublist
            print('Sublist ' + str(i + 1) + '/' + str(num_sublists) + ' translated')
            i = i + 1

        print('All sublists created and translated.')

        # flatten list of lists (create contiguous list out from the list of lists)
        flatlist = flatten(sublists)
        print('Lists flattened.')

        # insert each string in flattened list into new .ts
        create_new_text(filename, original_ts_path,
                        new_ts_path, pos_arr, flatlist, language)

        end = timer()
        print("Elapsed Time: " + str(timedelta(seconds=end-start)))
        print(filename + " finished.\n")


if __name__ == "__main__":
    main()
