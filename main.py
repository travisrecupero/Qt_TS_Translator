from deep_translator import GoogleTranslator
from lxml.html import fromstring
from secrets import subscription_key
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


# returns a random user agent to hide our actual browswer information
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

# returns a set or proxies that have Google and https capability
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

# using googletrans and microsoft api, return list
def translate_list(sub_list, language):
    retList = list()
    sleep(random.uniform(7, 10))
    for string in sub_list:
        sleep(1)
        string = transliterate(string)
        try:
            if ignore(string) is True:
                retList.append(string)
            else:
                if 'ch' in language:
                    language = 'zh-CN'
                    translated = str_to_chinese(string)
                    retList.append(translated)
                if 'es' in language:
                    translated = str_to_spanish(string)
                    retList.append(translated)
                else:
                    if 'ch' in language:
                        language = 'zh-CN'
                    translated = GoogleTranslator(
                        'en', language).translate(string)
                    retList.append(translated)
        except Exception:  # if element cant be translated just use original
            retList.append(string)
            pass
    return retList

# returns true if string is in constants.IGNORE_STRINGS
def ignore(string):
    ret_val = False
    string = string.split(' ')
    for substr in string:
        if substr in constants.IGNORE_STRINGS:
            ret_val = True
            return ret_val
    return False

# returns transliterated string if string is in constants.TRANSLITERATE_STRINGS
def transliterate(string):
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

# returns given english string as chinese
def str_to_chinese(ch_string):
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "eastus2"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'zh-Hans'
    }
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': str(ch_string)
    }]

    request = requests.post(
        constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    # Grab translated string
    text = response[0]['translations'][0]['text']

    return str(text)

# returns given english string as spanish
def str_to_spanish(string):
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # Add your location, also known as region. The default is global.
    # This is required if using a Cognitive Services resource.
    location = "eastus2"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'es'
    }
    constructed_url = endpoint + path

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
    start = timer()
    file_arr = []

    for file in os.listdir(constants.ORIGINAL_TS_PATH):
        file_arr.append(file)
    print(file_arr)

    # Leave chinese and spanish out until deployment.
    # Chinese translations use Azure Cloud Resource which have limited num of characters for translations
    # file_arr = ['t1_hi.ts'] # Declare only desired files OR leave commented line out to translate entire folder

    for filename in file_arr:
        language = filename[3:5]

        original_ts_path = constants.ORIGINAL_TS_PATH + filename
        new_ts_path = constants.NEW_TS_PATH + filename

        print('Working on ...' + language)

        master_list = extract_original_texts(
            filename, original_ts_path)  # every string to be translated

        print("Number of strings to be translated: " + str(len(master_list)))
        # line number of every translation occurence in .ts (starting at 0)
        pos_arr = count_trans_line_numbers(filename, original_ts_path)

        # can only translate lists with 15k characters
        # so we create list of lists with create_sublists(master_list, n), n = num of sublists
        sublists = create_sublists(master_list, constants.NUM_OF_SUBLISTS)
        print("Size of each(" + str(constants.NUM_OF_SUBLISTS) +
              ") sublist: " + str(len(sublists[0])))

        # translate each sublist
        i = 0
        for sublist in sublists:
            # translate each sublist
            sublist = translate_list(sublist, language)
            sublists[i] = sublist
            print('Sublist ' + str(i) + ' created')
            print("Sublist " + str(i) + " contents: " +
                  str(sublist[0]) + ", " + str(sublist[1]) + ", " + str(sublist[2]) + ". . .")
            i = i + 1

        print('All sublists created and translated.')

        # flatten list of lists (create contiguous list out from the list of lists)
        flatlist = flatten(sublists)
        print('Lists flattend.')
        print("flatlist = " + str(flatlist[0]) + ", " +
              str(flatlist[1] + ", " + str(flatlist[2])) + " . . .")

        # insert each string in flattened list into new .ts
        create_new_text(filename, original_ts_path,
                        new_ts_path, pos_arr, flatlist, language)

        end = timer()
        print("Elapsed Time (h.mm.ss.zzz): " +
              str(timedelta(seconds=end-start)))
        print("Program finished.")


if __name__ == "__main__":
    main()
