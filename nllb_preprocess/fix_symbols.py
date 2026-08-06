import os
import pandas as pd
import re
import unicodedata

latin_pattern = re.compile(r'[a-zA-Z]')
cyrillic_pattern = re.compile(r'[а-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]')


def count_unique_chars(word):
    latin_chars = set(latin_pattern.findall(word.lower()))
    cyrillic_chars = set(cyrillic_pattern.findall(word.lower()))

    return len(latin_chars), len(cyrillic_chars)


def analyze_words(sentences):
    latin_words = []
    mixed_words = []

    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)

        for word in words:
            lat_count, cyr_count = count_unique_chars(word)

            has_latin = lat_count > 0
            has_cyrillic = cyr_count > 0

            if has_latin and not has_cyrillic:
                latin_words.append(word)

            if has_latin and has_cyrillic:
                mixed_words.append(word)

    return list(set(latin_words)), list(set(mixed_words))


def find_lat_cyr_words(sents, print_latin=True):
    lat_words, lat_cyr_words = analyze_words(sents)
    if print_latin:
        print(f'Latin words = {len(lat_words)}')
        for word in lat_words:
            print(word)
            print()
        print(f'Latin words = {len(lat_cyr_words)}')
        print()

    print(f'Latin-cyrillic words = {len(lat_cyr_words)}')
    for word in lat_cyr_words:
        latin_chars = set(latin_pattern.findall(word))
        cyrillic_chars = set(cyrillic_pattern.findall(word))
        print(word)
        print(latin_chars)
        print(cyrillic_chars)
        print()
    print(f'Latin-cyrillic words = {len(lat_cyr_words)}')
    print()


def find_word_with_symbol(text, symbol):
    words = re.findall(r'\b\w*' + re.escape(symbol) + r'\w*\b', text)

    return sorted(set(words))


def find_context_with_symbol(text, symbol):
    examples = re.findall(r'.{0,15}' + re.escape(symbol) + r'.{0,15}', text)

    return sorted(set(examples))


def replace_lat_cyr_til_ru(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'a' in word and cyr_count > lat_count:
            word = word.replace('a', 'а')

        if lat_count == 1 and 'y' in word and cyr_count > lat_count:
            word = word.replace('y', 'у')

        if lat_count == 1 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'е')

        if lat_count == 1 and 'o' in word and cyr_count > lat_count:
            word = word.replace('o', 'о')

        if lat_count == 1 and 'p' in word and cyr_count > lat_count:
            word = word.replace('p', 'р')

        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_lat_cyr_til_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'O' in word and cyr_count > lat_count:
            word = word.replace('O', 'О')

        if lat_count == 1 and 'u' in word and cyr_count > lat_count:
            word = word.replace('u', 'ғ')

        if lat_count == 1 and 'I' in word and cyr_count > lat_count:
            word = word.replace('I', 'І')

        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_til_ru(text):
    old_new_dict = {'O': 'О',
                    'H': 'Н',
                    'Xусхун': 'Хусхун',
                    'Xаным': 'Ханым',
                    'Xырначах': 'Хырначах',
                    ' \xad ': '',
                    '\xa0': ' ',
                    '\u2009': ' ',
                    '\u202f': ' ',
                    '&amp; #': ' ',
                    '&amp; quot ;': ' ',
                    'Двoe': 'Двое',
                    'Дeвa': 'Дева',
                    'Мoгy': 'Могу',
                    'Нo': 'Но',
                    'Хьrлыс': 'Хылыс',
                    'ѐ': 'е',
                    'ѝ': 'и',
                    'Prіma': 'Prima',
                    'Secunda': 'Secunda',
                    'Tertіa': 'Tertia',
                    'ХI': 'XI',
                    'ХV': 'XV',
                    'І': 'I',
                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def replace_til_kjh(text):
    old_new_dict = {'Ӌ': 'Ҷ',
                    'ӌ': 'ҷ',
                    '&amp; #': ' ',
                    '&amp; quot ;': ' ',
                    'VІІІ': 'VIII',
                    'XVІІ': 'XVII',
                    'ІV': 'IV',
                    'Xыс': 'Хыс',
                    'VІІ': 'VII',
                    'ІX': 'IX',
                    'Xолын': 'Холын',
                    'Xырнаҷах': 'Хырнаҷах',
                    'Tеrtіа': 'Tertia',
                    'VІ': 'VI',
                    'XІІ': 'XII',
                    'Prіmа': 'Prima',
                    'Sесundа': 'Secunda',
                    'Xалазахтарны': 'Халазахтарны',
                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def fix_til():
    path = '/home/adeshkin/khakas_projects/data/translation/til_corpus/para/til_para_corpus.csv'
    save_path = '../data/til_para_corpus_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: replace_til_ru(x.strip()))
    df['Русский'] = df['Русский'].apply(lambda x: replace_lat_cyr_til_ru(x).strip())

    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_til_kjh(x.strip()))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_til_kjh(x).strip())

    sents = df['Хакасский'].tolist()

    find_lat_cyr_words(sents)

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '':
        examples = find_word_with_symbol(text, symbol)
        # examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            print(*examples, sep='\n')
            print()

    df.to_csv(save_path, index=False)


def replace_v1(text):
    old_new_dict = {
        'Мaилc': 'Маилс',
        '_x001f_': '',

        'значокOffice2003': 'значок Office2003',
        'Pоl': 'Pol',
        'KBBarостается': 'KBBar остается',
        'PCсодержит': 'PC содержит',
        'ЕСТS': 'ECTS',
        'Rules2присоединиться': 'Rules2 присоединиться',
        'AIXTHREAD_SPINLOзначение': 'AIXTHREAD_SPINLO значение',
        'консультацииt': 'консультации',
        'ТV': 'TV',
        'фaйлoв': 'файлов',
        'Taмпоны': 'Тампоны',
        'использующегоSetCursorPosфункция': 'использующего SetCursorPos функция',
        'yл': 'ул',
        'girlКто': 'girl Кто',
        'sстр': 'sctp',
        'Slicerполучает': 'Slicer получает',
        '0кk': '0kk',
        'sequencesи': 'sequencesu',
        'Apыштaeве': 'Арыштаеве',
        'UСL': 'UCL',

        'пaнeли': 'UCL',
        'отendzone': 'otendzone',
        'Оil': 'Oil',
        'разрешеноJune': 'разрешено June',
        'VІІ': 'VII',
        'СNN': 'CNN',

        'ffmpеg': 'ffmpeg',
        'введитеMMC': 'введите MMC',
        'Vargцn': 'Vargun',
        'Tяmiri': 'Tamiri',
        'гаrden': 'rarden',

        'пo': 'по',
        'Apыштaeва': 'Арыштаева',
        'Apыштaeв': 'Арыштаев',
        'ХIV': 'XIV',
        'VІ': 'VI',
        'ХХI': 'XXI',
        'VIIІ': 'VIII',

        'черезTwinCAT': 'через TwinCAT',
        'междунаpоднoго': 'международного',
        'Saгa': 'Sara',
        'ХML': 'XML',
        'командуOk': 'команду Ok',
        'СD': 'CD',
        'XIІ': 'XII',

        'студииSummitне': 'студии Summit не',
        'нeпосpeдствeннo': 'непосредственно',
        'Hо': 'Но',
        'типаMS220kr': 'типа MS 220 кг',
        'Pу40': 'Py40',
        'кнопкуOk': 'кнопку Ok',
        'vbи': 'vbu',
        'Сomputex': 'Computex',

        'Hе': 'Не',
        'утеlение': 'утешение',
        'значокAddinsec': 'значок Addinsec',
        'обработчикиClickInиClickOutсобытияCirc3': 'обработчики ClickInиClickOut события Circ3',
        'IMPORTкофеварка': 'IMPORT кофеварка',
        'Таверныs': 'Таверны',
        'ПАКЕТЬI': 'ПАКЕТЫ',
        'клавишуReturn': 'клавишу Return',
        'IPSecSelectPPTPзатем': 'IPSecSelectPPTP затем',
        'Pцttinger': 'Puttinger',

        'Бунниposted': 'Бунни posted',
        'посетитеHeviz': 'посетите Heviz',
        'Тhomas': 'Thomas',
        'ссылкуGPEditDebugLevel': 'ссылку GPEditDebugLevel',
        'памятиBenly': 'памяти Benly',
        'PDFфайлы': 'PDF файлы',
        'командуDelete': 'команду Delete',

        'системаWindows': 'система Windows',
        'элacтическая': 'эластическая',
        'XIIІ': 'XIII',
        'СКИДKA': 'СКИДКА',
        'Kaкие': 'Какие',
        'мышиService1': 'мыши Service1',

        'Рh': 'Ph',
        'Bт': 'Вт',
        'nскажет': 'скажет',
        'kг': 'кг',
        'видeo': 'видео',
        'МVV': 'MVV',

        'МBА': 'MBA',
        'pиre': 'pure',
        'AФ': 'АФ',
        'мышиNSPI': 'мыши NSPI',

        'Taйвань': 'Тайвань',
        'CЄобязателен': 'CЄ обязателен',
        'Bы': 'Вы',
        '\xa0': ' ',
        '\xad ': '',
        '\xad': '',
        '\u202f': ' ',
        '\u200b': ' ',
        '\u200c': ' ',
        '\ufeff': ' ',
        'stуlе': 'style',

        'Ӱthӱrnӱt': 'Ethernet',
        'PDFфайлларға': 'PDF файлларға',
        'Vаrgцn': 'Vargun',
        'АМD': 'AMD',
        'Nоғысчыларның': 'Тоғысчыларның',
        'Dіsnӱң': 'Disney',

        'Mіхеd': 'Mixed',
        'Nа': 'Na',
        'gсс': 'gcc',
        'чӧрібіскЕN': 'чӧрібіскен',
        'НАSS': 'HASS',
        'Dғmіo': 'Dumio',
        'XІІІ': 'XIII',
        'НDRІ': 'HDRI',
        'pу': 'py',
        'DRMі0': 'DRMi0',
        'Rғn': 'Run',
        'SеtСursorPosфункция': 'SеtСursorPos функция',
        'РR': 'PR',
        'оnlіnе': 'online',
        'пӧзіr': 'пӧзік',
        'Lіtӱ': 'Lite',
        'sӱqғӱnсӱsи': 'sequencesu',
        'ҶVI': 'XVI',
        'Tяmіrі': 'Tamіrі',
        'ііg': 'iig',

        'Tайвань': 'Тайвань',
        'Іnfozoіdох': 'Infozoidox',
        'Fе': 'Fe',
        'ХРS': 'XPS',
        'Oл': 'Ол',
        'НV': 'HV',
        'пілдірібіскЕN': 'пілдірібіскен',
        'Іntӱrnӱt': 'Internet',
        'PvPойыннар': 'PvP ойыннар',
        'Pцttіngеr': 'Puttinger',

        'ІMPORTкофепызырҷаң': 'ІMPORT кофе пызырҷаң',
        'Strееt': 'Street',
        'lдӧк': 'Ідӧк',
        'сlғb': 'club',
        'twіttеr': 'twitter',
        'Wіfӱ': 'Wifi',
        'ХХVIII': 'XXVIII',
        'іnІғsіnӱss': 'inBusiness',
        'Аgӱnt': 'Agent',
        'gіrlхыстар': 'gіrl хыстар',
        'Lіnғҷ': 'Linux',
        'Оіl': 'Oil',
        'идеріlt': 'идері',
        'Іntеl': 'Intel',
        'Аndroіdtі': 'Аndroіdті',

        'Іstsnіғl': 'Istanbul',
        'закyска': 'закуска',
        'і20GB': 'i20GB',
        'ХІV': 'XIV',
        'Flғsh': 'Flush',
        'ТF': 'TF',
        'салғаm': 'салғам',
        'отеndzonенаң': 'otendzoneнаң',

        'МЕS': 'MES',
        'Dӱmoldӱrпользовательнең': 'Demolder пользовательнең',
        'СМОS': 'CMOS',
        'Аvаst': 'Avast',
        'МОF': 'MOF',
        'ХVII': 'XVII',
        'ӰN': 'ӰН',
        'ІV': 'IV',
        'SМS': 'SMS',
        'КееРаss': 'KeePass',
        'СУРЫF': 'СУРЫҒ',
        'ЕXБ': 'ЕХБ',
        'Ғsӱr': 'User',
        'Іv': 'IV',
        'thе': 'the',
        'SеtСursorPos': 'SetCursorPos',
        'Tее': 'Tee',
        'аurеus': 'aureus',
        'сtх': 'ctx',
        'Іzеn': 'Izen',

        'lіvӱ': 'live',
        'Rӱаpӱr': 'Reaper',
        'vіltа': 'vilta',
        'ӧӧніlt': 'ӧӧні',

        'СSS': 'CSS',
        'Сіrс3': 'Circ3',
        'Vинсент': 'Винсент',
        'сomда': 'сомда',
        'Mының': 'Мының',
        'парt': 'пар',
        'Tӱгеде': 'Тӱгеде',
        'shаrӱwаrӱ': 'shareware',
        'ЕВS': 'EBS',
        'FАSTидентификациязы': 'FАST идентификациязы',
        'іntӱrfасӱ': 'interface',
        'dӱ': 'de',
        'іӱtа': 'ieta',
        'ІDЕ': 'IDE',
        'Еntеrклавишаны': 'Еntеr клавишаны',
        'Mассар': 'Macсар',
        'ХЫFЫРЫҢАР': 'ХЫҒЫРЫҢАР',
        'АІLА': 'AILA',
        'ӱntӱrprіsӱ': 'enterprise',
        'Аpыштаев': 'Арыштаев',
        'чарадылчаӦғnӱ': 'чарадылча June',
        'іlе': 'ile',
        'ЕSRІ': 'ESRI',
        'ССFL': 'CCFL',
        'FАST': 'FAST',
        'Еntеr': 'Enter',
        'ӦҒnіt': 'JUnit',
        'тыығfан': 'тыыған',
        'Ӧғn': 'Jun',
        'сlғb': 'club',
        'А8L': 'A8L',
        'АОL': 'AOL',
        'Tamіrі': 'Tamiri',
        'kӱң': 'key',
        'фильтіhдең': 'фильтрдең',
        'gіrl': 'girl',
    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def replace_lat_cyr_v1_ru(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if cyr_count == 1 and 'а' in word and lat_count > cyr_count:
            word = word.replace('а', 'a')

        if cyr_count == 1 and 'А' in word and lat_count > cyr_count:
            word = word.replace('А', 'A')

        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')

        if lat_count == 1 and 'H' in word and cyr_count > lat_count:
            word = word.replace('H', 'Н')

        if lat_count == 1 and 'x' in word and cyr_count > lat_count:
            word = word.replace('x', 'х')

        if lat_count == 1 and 'y' in word and cyr_count > lat_count:
            word = word.replace('y', 'у')

        if lat_count == 1 and 'a' in word and cyr_count > lat_count:
            word = word.replace('a', 'а')

        if lat_count == 1 and 'T' in word and cyr_count > lat_count:
            word = word.replace('T', 'Т')

        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')

        if lat_count == 1 and 'e' in word and cyr_count > lat_count:
            word = word.replace('e', 'е')

        if lat_count == 1 and 'o' in word and cyr_count > lat_count:
            word = word.replace('o', 'о')

        if lat_count == 1 and 'p' in word and cyr_count > lat_count:
            word = word.replace('p', 'р')

        if lat_count == 1 and 'K' in word and cyr_count > lat_count:
            word = word.replace('K', 'К')

        if lat_count == 1 and 'A' in word and cyr_count > lat_count:
            word = word.replace('A', 'А')

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_lat_cyr_v1_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if cyr_count == 1 and 'ӱ' in word and lat_count > cyr_count:
            word = word.replace('ӱ', 'e')
        if cyr_count == 1 and 'u' in word and lat_count > cyr_count:
            word = word.replace('u', 'ғ')

        if lat_count == 1 and 'x' in word and cyr_count > lat_count:
            word = word.replace('x', 'х')

        if lat_count == 1 and 'o' in word and cyr_count > lat_count:
            word = word.replace('o', 'о')

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def fix_v1():
    path = '/home/adeshkin/khakas_projects/data/translation/parallel_corpus/khakas_russian_parallel_corpus_v1.csv'
    save_path = '../data/khakas_russian_parallel_corpus_v1_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)

    print(len(df))
    df = df[~df['Хакасский'].str.contains('Sпsса новки')]
    print(len(df))

    df['Русский'] = df['Русский'].apply(lambda x: replace_v1(x.strip()))
    df['Русский'] = df['Русский'].apply(lambda x: replace_lat_cyr_v1_ru(x).strip())

    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_v1(x.strip()))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_v1_kjh(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_v1(x).strip())

    sents = df['Хакасский'].tolist()

    # find_lat_cyr_words(sents, print_latin=False)

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in ['\xa0', '\xad', '\u200b']:
        # examples = find_word_with_symbol(text, symbol)
        examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            # print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()

    df.to_csv(save_path, index=False)


def replace_lat_cyr_vkloc_ru(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_lat_cyr_vkloc_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_vkloc_kjh(text):
    old_new_dict = {'ӊ': 'ң',
                    'ӌ': 'ҷ',
                    'Ӏ': 'І',

                    'Ö': 'Ӧ',
                    'ö': 'ӧ',
                    'ÿ': 'ӱ',
                    'скipiг': 'скіріг',
                    'зi': 'зі',
                    'нi': 'ні',
                    'Iр': 'Ір',
                    'таpтып': 'тартып',

                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def fix_vkloc():
    path = '/home/adeshkin/khakas_projects/data/translation/vkloc/vkloc.csv'
    save_path = '../data/vkloc_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)

    df['Русский'] = df['Русский'].apply(lambda x: replace_lat_cyr_vkloc_ru(x).strip())

    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_vkloc_kjh(x.strip()))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_vkloc_kjh(x).strip())

    sents = df['Хакасский'].tolist()

    find_lat_cyr_words(sents, print_latin=False)

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіғңҷӦӧӰӱ' == 'ІіғңҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '':
        examples = find_word_with_symbol(text, symbol)
        # examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()

    df.to_csv(save_path, index=False)


def replace_lat_cyr_ecorpus_kjh(text):
    def replace_match(match):
        word = match.group(0)

        lat_count, cyr_count = count_unique_chars(word)

        if lat_count == 1 and 'i' in word and cyr_count > lat_count:
            word = word.replace('i', 'і')

        if lat_count == 1 and 'I' in word and cyr_count > lat_count:
            word = word.replace('I', 'І')

        if lat_count == 1 and 'C' in word and cyr_count > lat_count:
            word = word.replace('C', 'С')

        if lat_count == 1 and 'c' in word and cyr_count > lat_count:
            word = word.replace('c', 'с')

        if lat_count == 1 and 'O' in word and cyr_count > lat_count:
            word = word.replace('O', 'О')

        return word

    pattern = r'[a-zA-Zа-яА-ЯёЁІіҒғҢңҶҷӦӧӰӱ]+'
    return re.sub(pattern, replace_match, text)


def replace_ecorpus_kjh(text):
    # ІіҒғҢңӦӧӰӱ
    old_new_dict = {
        'ӌ': 'ҷ',
        'Ӏ': 'І',
        'Ӌ': 'Ҷ',
        '\xad': '',
        '\u200e': ' ',

        'XІІ': 'XII',
        'VІІІ': 'VIII',
        'XVІІ': 'XVII',
        'VІ': 'VI',
        'ІV': 'IV',
        'Xолын': 'Холын',
        'Prіma': 'Prima',
        'ІX': 'IX',
        'Xалазахтарны': 'Халазахтарны',

        'XІ': 'XI',
        'Tertіa': 'Tertia',
        'iкi': 'ікі',
        'Iкi': 'Ікі',
        'VIІ': 'VII',
    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def replace_ecorpus_ru(text):
    old_new_dict = {'\xad': '',
                    'ѐ': 'е',
                    'ѝ': 'и',

                    'ууcа': 'ууса',
                    'китайcких': 'китайских',
                    'Tertіa': 'Tertia',
                    'ХVІІ': 'XVII',
                    'ХIII': 'XIII',
                    'Prіma': 'Prima',
                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def fix_ecorpus():
    path = '/home/adeshkin/khakas_projects/data/translation/e_corpus/e_corpus.csv'
    save_path = '../data/e_corpus_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)

    df['Русский'] = df['Русский'].apply(lambda x: replace_ecorpus_ru(x).strip())

    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_ecorpus_kjh(x.strip()))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_lat_cyr_ecorpus_kjh(x).strip())

    sents = df['Хакасский'].tolist()

    find_lat_cyr_words(sents, print_latin=False)

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in 'IPSTVXacdeimnrtux':
        examples = find_word_with_symbol(text, symbol)
        # examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()

    df.to_csv(save_path, index=False)


def replace_klr_kjh(text):
    old_new_dict = {
        'ӊ': 'ң',
        ' \xad ': '',
        '\u200e': ' ',
        '\u206a': ' ',
        'ö': 'ӧ',
        'ÿ': 'ӱ',
        'ӏ': 'і',

    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def replace_klr_ru(text):
    old_new_dict = {' \xad ': '',
                    'ѐ': 'е',
                    'ѝ': 'и',
                    'ӌ': 'ҷ',
                    }

    for ch1, ch2 in old_new_dict.items():
        text = re.sub(ch1, ch2, text)

    return text


def fix_klr():
    path = '/home/adeshkin/khakas_projects/data/translation/khakas-language-resources/klr.csv'
    save_path = '../data/klr_fix_symbols.csv'
    assert not os.path.exists(save_path)
    df = pd.read_csv(path)

    df['Русский'] = df['Русский'].apply(lambda x: replace_klr_ru(x).strip())
    df['Хакасский'] = df['Хакасский'].apply(lambda x: replace_klr_kjh(x.strip()).strip())

    sents = df['Хакасский'].tolist()

    find_lat_cyr_words(sents, print_latin=False)

    text = ' '.join(sents)
    print(repr(''.join(sorted(set(text)))))
    print()

    assert 'ІіҒғҢңҶҷӦӧӰӱ' == 'ІіҒғҢңҶҷӦӧӰӱ'  # ІіҒғҢңҶҷӦӧӰӱ

    for symbol in '|':
        # examples = find_word_with_symbol(text, symbol)
        examples = find_context_with_symbol(text, symbol)

        if len(examples) > 0:
            print(repr(symbol))
            print(unicodedata.name(symbol))
            print(len(examples))
            # print(*examples, sep='\n')
            print(examples)
            print()

    df.to_csv(save_path, index=False)


if __name__ == '__main__':
    fix_til()
    fix_v1()
    fix_vkloc()
    fix_ecorpus()
    fix_klr()
