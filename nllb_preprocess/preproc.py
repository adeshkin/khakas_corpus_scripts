# based on https://github.com/facebookresearch/stopes/blob/2be1bb8f67a38588eef3dfce204679d180a2c921/stopes/pipelines/monolingual/monolingual_line_processor.py#L214
import re
import sys
import unicodedata
from sacremoses import MosesPunctNormalizer
import pandas as pd

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


def main():
    path = '../data/khakas_russian_parallel_corpus_v1_fix_symbols_drop.csv'
    save_path = '../data/kv1_done.csv'
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: preproc_data(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df['Источник'] = df['Источник'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)

    path = '../data/til_para_corpus_fix_symbols_drop.csv'
    save_path = '../data/til_done.csv'
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: preproc_data(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)

    path = '../data/e_corpus_fix_symbols_drop.csv'
    save_path = '../data/ec_done.csv'
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: preproc_data(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df['Источник'] = df['Источник'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)

    path = '../data/vkloc_fix_symbols_drop.csv'
    save_path = '../data/vl_done.csv'
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: preproc_data(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)

    path = '../data/klr_fix_symbols_drop.csv'
    save_path = '../data/klr_done.csv'
    df = pd.read_csv(path)
    df['Русский'] = df['Русский'].apply(lambda x: preproc_data(x))
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df['Источник'] = df['Источник'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)


def main_mono():
    path = '../data/mono_fix_symbols_drop.csv'
    save_path = '../data/mono_done.csv'
    df = pd.read_csv(path)
    df['Хакасский'] = df['Хакасский'].apply(lambda x: preproc_data(x))
    df['Источник'] = df['Источник'].apply(lambda x: preproc_data(x))
    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    main_mono()
