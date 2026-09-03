# based on https://github.com/facebookresearch/stopes/blob/2be1bb8f67a38588eef3dfce204679d180a2c921/stopes/pipelines/monolingual/monolingual_line_processor.py#L214
import re
import sys
import unicodedata
from sacremoses import MosesPunctNormalizer, MosesDetokenizer
import pandas as pd

md = MosesDetokenizer(lang='ru')
mpn = MosesPunctNormalizer(lang="en")
mpn.substitutions = [(re.compile(r), sub) for r, sub in mpn.substitutions]


def get_non_printing_char_replacer(replace_by: str = " "):
    non_printable_map = {
        ord(c): replace_by
        for c in (chr(i) for i in range(sys.maxunicode + 1))
        # same as \p{C} in perl
        # see https://www.unicode.org/reports/tr44/#General_Category_Values
        if unicodedata.category(c) in {"C", "Cc", "Cf", "Cs", "Co", "Cn"}
    }

    def replace_non_printing_char(line) -> str:
        return line.translate(non_printable_map)

    return replace_non_printing_char


replace_nonprint = get_non_printing_char_replacer(" ")


def preproc_data(text):
    clean = mpn.normalize(text)
    clean = replace_nonprint(clean)
    # replace 𝓕𝔯𝔞𝔫𝔠𝔢𝔰𝔠𝔞 by Francesca
    clean = unicodedata.normalize("NFKC", clean)

    return clean.strip()


def detok_space_norm(text):
    tokens = text.split()
    text = md.detokenize(tokens)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


source2info = {'Англо-русский корпус Яндекса': ('Examples from Yandex English-Russian Parallel Corpus (version 1.3)',
                                                'Примеры из Англо-русского параллельный корпус Яндекса (версия 1.3)',
                                                'multi-domain',
                                                'многодоменный',
                                                'ru',
                                                'https://translate.yandex.ru/corpus'
                                                ),
               'Учебники, статьи, пьесы': ('School textbooks, scientific articles, literature',
                                           'Школьные учебники, научные статьи, литература',
                                           'education',
                                           'образование',
                                           'kjh',
                                           'none'
                                           ),
               'til': ('Examples from TIL corpus',
                       'Примеры из TIL корпус',
                       'multi-domain',
                       'многодоменный',
                       'kjh_ru',
                       'https://github.com/turkic-interlingua/til-mt/tree/master/til_corpus',
                       ),
               'khakas-language-resources': ('Processed examples from the electronic corpus of the Khakas language',
                                             'Обработанные примеры из электронного корпуса хакасского языка',
                                             'multi-domain',
                                             'многодоменный',
                                             'kjh_ru',
                                             'https://github.com/adeshkin/khakas-language-resources',
                                             ),
               'Новый завет. Евангелия и деяния': ('New Testament (Gospels, Acts)',
                                                   'Новый Завет (Евангелия, Деяния)',
                                                   'bible',
                                                   'библия',
                                                   'ru',
                                                   'https://khakas.altaica.ru'
                                                   ),
               'Новый завет. Послания и открове': ('New Testament (Epistles, Revelation)',
                                                   'Новый Завет (Послания, Откровение)',
                                                   'bible',
                                                   'библия',
                                                   'ru',
                                                   'https://khakas.altaica.ru'
                                                   ),
               'Статьи Н. Ф. Трошкина 1': (
                   'My memoirs [collection of articles from the newspaper "Khakas chiri"/ "Khabar"]. Part 1. N.F. Troshkin',
                   'Мои воспоминания [сборник статей из газеты "Хакас чирі"/ "Хабар"]. Часть 1. Н.Ф. Трошкин',
                   'newspaper article',
                   'газетная статья',
                   'kjh',
                   'https://khakas.altaica.ru'
               ),
               'Статьи Н. Ф. Трошкина 2': (
                   'My memoirs [collection of articles from the newspaper "Khakas chiri"/ "Khabar"]. Part 2. N.F. Troshkin',
                   'Мои воспоминания [сборник статей из газеты "Хакас чирі"/ "Хабар"]. Часть 2. Н.Ф. Трошкин',
                   'newspaper article',
                   'газетная статья',
                   'kjh',
                   'https://khakas.altaica.ru'
               ),
               'katanov 1 folklore': (
                   'Dialects of the Uriankhai (Soyots), Abakan Tatars and Karagas. Texts collected and translated by N.F. Katanov. St. Petersburg, 1907. (Samples of folk literature of the Turkic tribes, published by V. Radlov. — Part IX)',
                   'Наречия урянхайцев (сойотов), абаканских татар и карагасов. Тексты, собранные и переведенные Н.Ф. Катановым. Санкт-Петербург, 1907. (Образцы народной литературы тюркских племен, изданные В. Радловым. — Ч. IX)',
                   'folklore',
                   'фольклор',
                   'kjh',
                   'https://khakas.altaica.ru'
               ),
               'грамматика': ('Examples from the "Grammar of the Khakas language" 1975.',
                              'Примеры из «Грамматики хакасского языка» 1975 г.',
                              'education',
                              'образование',
                              'kjh',
                              'https://khakas.altaica.ru'
                              ),
               'чатхан': ('Khaykhastyg chatkhan [Magic chatkhan]. I.P. Topoev',
                          'Хайхастығ чатхан [Волшебный чатхан]. И.П. Топоев',
                          'play (literature)',
                          'пьеса',
                          'kjh',
                          'https://khakas.altaica.ru'
                          ),
               'алиса': ('Alisanyn Khaykhastar Chirinzer chorygy [Alice in Wonderland]',
                         'Алисаның Хайхастар Чирінзер чорығы [Алиса в стране чудес]',
                         'story (literature)',
                         'повесть',
                         'ru',
                         'https://khakas.altaica.ru'
                         ),
               'ОЛҒАННАРЫ': ('Pistin aalnyn olgannary [Rebyata nashego aala]. G.G. Kazachinova',
                             'Пістің аалның олғаннары [Ребята нашего аала]. Г.Г. Казачинова',
                             'collection of short stories and essays',
                             'сборник рассказов и очерков',
                             'kjh',
                             'https://khakas.altaica.ru'
                             ),
               'СЫЫН': ('Syyn muuzi [Marali roga]. V.G. Shulbayeva',
                        'Сыын мӱӱзі [Маральи рога]. В.Г. Шулбаева',
                        'play (literature)',
                        'пьеса',
                        'kjh',
                        'https://khakas.altaica.ru',
                        ),
               'По дорогам предков 2': ('Obekelernin chollaryncha [Po dorogam predkov]. Part 2. L.I. Chebodaeva',
                                        'Ӧбекелернің чолларынҷа [По дорогам предков]. Часть 2. Л.И. Чебодаева',
                                        'collection of short stories and essays',
                                        'сборник рассказов и очерков',
                                        'kjh',
                                        'https://khakas.altaica.ru'
                                        ),
               'По дорогам предков 1': ('Obekelernin chollaryncha [Po dorogam predkov]. Part 1. L.I. Chebodaeva',
                                        'Ӧбекелернің чолларынҷа [По дорогам предков]. Часть 1. Л.И. Чебодаева',
                                        'collection of short stories and essays',
                                        'сборник рассказов и очерков',
                                        'kjh',
                                        'https://khakas.altaica.ru'
                                        ),
               'Художественное произведение': ('Collection of literary works',
                                               'Сборник литературных произведений',
                                               'literature',
                                               'литература',
                                               'kjh',
                                               'none'
                                               ),
               'честь': ('Khakastarnyn posty uluglir kiktezi [Kodeks chesti khakasov]. V.M. Torosov',
                         'Хакастарның посты улуғлир киктезі [Кодекс чести хакасов]. В.М. Торосов',
                         'essay',
                         'очерк',
                         'kjh',
                         'https://khakas.altaica.ru'
                         ),
               'vl': ('Social network interface',
                      'Интерфейс социальной сети',
                      'technical',
                      'технический',
                      'ru',
                      'none'
                      ),
               }


def main_final_para():
    path = '../data/kjh_ru_dedup.csv'
    save_path = '../data/final/para_kjh_ru_final.csv'
    df = pd.read_csv(path)
    df['Хакасский'] = df['Хакасский'].apply(lambda x: detok_space_norm(preproc_data(detok_space_norm(x))))
    df['Русский'] = df['Русский'].apply(lambda x: detok_space_norm(preproc_data(detok_space_norm(x))))
    df['Источник'] = df['Источник'].apply(lambda x: detok_space_norm(preproc_data(x)))
    df['Файл'] = df['Файл'].apply(lambda x: detok_space_norm(preproc_data(x)))
    print(df.columns)
    df = df[['Хакасский', 'Русский', 'Источник']]
    df = df.rename(columns={'Хакасский': 'kjh',
                            'Русский': 'ru',
                            'Источник': 'source'
                            })

    print(df['source'].value_counts())
    column_names = ['name', 'ru_name', 'domain_or_genre', 'ru_domain_or_genre', 'source_language', 'url']

    for i, col in enumerate(column_names):
        df[col] = df['source'].map(lambda x: source2info[x][i])

    df = df.drop(columns=['source'])
    df = df.rename(columns={'name': 'source_name_en',
                            'ru_name': 'source_name_ru',
                            'domain_or_genre': 'domain_en',
                            'ru_domain_or_genre': 'domain_ru',
                            'url': 'source_url',
                            })
    url2id = {'none': 'khakas-materials',
              'https://translate.yandex.ru/corpus': 'en-ru-ya-corpus',
              'https://khakas.altaica.ru': 'khakas-altaica-ru',
              'https://github.com/adeshkin/khakas-language-resources': 'khakas-lang-res',
              'https://github.com/turkic-interlingua/til-mt/tree/master/til_corpus': 'til-corpus',
              }
    df['source_id'] = df['source_url'].apply(lambda x: url2id[x])

    for col in df.columns:
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df.to_csv(save_path, index=False)


def main_final_mono():
    path = '../data/mono_kjh_dedup.csv'
    save_path = '../data/final/mono_kjh.csv'
    df = pd.read_csv(path)
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(detok_space_norm(x)))
    df['Источник'] = df['Источник'].apply(lambda x: preproc_data(x))
    df['Файл'] = df['Файл'].apply(lambda x: preproc_data(x))
    print(df.columns)
    df = df[['Хакасский', 'Источник', 'Файл']]
    df = df.rename(columns={'Хакасский': 'kjh',
                            'Источник': 'source',
                            'Файл': 'file',
                            })

    print(df['source'].value_counts())
    print(df['file'].value_counts())
    df.to_csv(save_path, index=False)


def main_final_final_mono():
    path = '../data/final/mono_kjh.csv'
    save_path = '../data/final/mono_kjh_final.csv'
    df = pd.read_csv(path)

    source_dict = {'khakaschiry': 'Articles from "Khakas Chiry" newspaper',
                   'raznoe': 'Texts from school textbooks, scientific articles, literature',
                   'vk_ah_tashyl': 'User posts from social networks'}
    df['source'] = df['source'].apply(lambda x: source_dict[x])

    df = df.drop(columns=['file', 'bad'])

    print(df.columns)

    for col in df.columns:
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df['len'] = df['kjh'].apply(lambda x: len(x))

    from razdel import tokenize
    def get_word_count(text):
        tokens = list(tokenize(text))
        words = [token.text for token in tokens if any(c.isalpha() for c in token.text)]

        return len(words)

    df['kjh_wlen'] = df['kjh'].apply(lambda x: get_word_count(x))
    print(df['kjh_wlen'].describe())
    print(sum(df['kjh_wlen'].tolist()))

    for col in df.columns:
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())
    print(df['source'].value_counts(normalize=True))
    df.to_csv(save_path, index=False)


def main_final_smol():
    df1 = pd.read_csv('/home/adeshkin/khakas_projects/khakas_corpus_scripts/smol/smoldoc/smoldoc_kjh.csv')
    print(df1.columns)
    df1 = df1.rename(columns={'Translation АНИСИМОВ': 'ru'})
    df = df1[['en', 'ru', 'kjh']].copy()
    for col in df.columns:
        print(col)
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df.to_csv('/home/adeshkin/Downloads/smoldoc_final_fix_finalize.csv', index=False)


def main_final_towns_villages():
    df1 = pd.read_csv('/home/adeshkin/Downloads/населенные пункты РХ - населенные пункты РХ_fix.csv')
    print(df1.columns)
    df = df1.rename(columns={'Русский': 'ru', 'Хакасский': 'kjh'})
    for col in df.columns:
        print(col)
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df.to_csv('/home/adeshkin/Downloads/населенные пункты РХ - населенные пункты РХ_fix_finalize.csv', index=False)


def main_final_cv():
    df = pd.read_csv('/home/adeshkin/Downloads/common_voice - life_fix.csv')
    print(df.columns)
    for col in df.columns:
        print(col)
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df.to_csv('/home/adeshkin/Downloads/common_voice - life_fix_finalize.csv', index=False)


def main_ru_kjh_base():
    df = pd.read_csv("/home/adeshkin/Downloads/diversity500_khakas.xlsx - Лист1.csv")
    print(df.columns)
    for col in df.columns:
        print(col)
        df[col] = df[col].apply(lambda x: detok_space_norm(preproc_data(x)).strip())

    df.to_csv("/home/adeshkin/Downloads/diversity500_khakas.xlsx - Лист1_finalize.csv", index=False)

if __name__ == '__main__':
    main_ru_kjh_base()
