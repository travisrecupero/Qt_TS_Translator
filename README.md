# SWE_TS_Translator

**Application Statement:** 
Qt Applications have the ability to generate .ts files (translation files). The files are in an xml format; they are turned into .qm files (binary files) which lets Qt read the xml and inserts translation where they are needed. Companies hire translators unless they have in-house translators, who will use Qt Linguist. Qt Linguist is a software that reads .ts files and allows the hired translator to manually insert translations. 

**Purpose:**
Automating the translation process by running a script that utilizes an online translation API. This will produce finished .ts files for Qt Applications. 

## Usage

Install the latest version of Python on your machine. The following instructions are for Linux/WSL users. If you run into dependency or Poetry issues please refer to https://python-poetry.org/docs/.
- First run `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
` to install Poetry
- Test to verify its installed with `poetry --version`
    - You can also run `where poetry` which should output ->  C:\Users\your_username\AppData\Local\Programs\Python\Python39\Scripts\poetry.exe depending on where your python is installed.
    - IF `bash: poetry: command not found` error try the following:
        - Add Poetry's bin directory (C:\Users\your_username\AppData\Roaming\Python\Scripts) in your `PATH`
environment variable.
- Run `poetry install` to install dependencies from the `poetry.lock` (file included in the repo)
- Lastly, run `poetry run python main.py`, the run command executes the given command inside the project’s virtualenv.


## Remarks

-   please note that this API only allows 5k _character_ translations per API call. Therefore, we shall make use of dividing lists into chunks, then later flattening the list back to normal.
-   the program has a slow runtime due to the API calls; we `sleep(1)` between each string translation and `sleep(random.uniform(7, 10))` between each sublist. 
-   The `.\translations\unfinished` folder contains sample `.ts` files. After execution, there will be `.ts` files created in `\translations\finished`. There you will find files identical to those contained in `\translations\unfinished`, BUT with translations inserted on every line that contained `<translation type="unfinished"></translation>`. I left `\translations\unfinished` to show the expected output.
-   if there is a timeout or a translation cannot be found we default to English
-   `constants.py` can be used to ignore or transliterate certain strings during translation. Transliteration lets us manipulate the string before translating to get better translations. (Sometimes a sentence in English can be one character or fewer words in another language.)
-   deep_translator API is buggy with Spanish and Chinese, so for those translations we use Microsoft Translator from Azure. The API key can be stored in `secrets.py`. Microsoft Translator costs money, so if you want free translations comment out the lines using `str_to_spanish(string)` and `str_to_chinese(string)`. (deep_translator may work now)


In Qt, run the following commands:
1. If you are using the finished .ts included in the repo then skip to step 2. Depending on the name of your .pro and the name you want for your .ts files, this command will use different arugments (they should generally be the same). This generates .ts files based on your .ui files.
- `lupdate Appplication.pro -ts t1_fr.ts t1_sp.ts`
2. The following command will generate .qm files based off of .ts files. These .qm's will give Qt binary files to compile with.
- `lrelease t1_fr.ts t1_sp.ts`

The documentation to this translation API can be found here: https://github.com/nidhaloff/deep-translator
