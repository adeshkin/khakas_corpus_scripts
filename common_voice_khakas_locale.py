import pandas as pd
import os
import glob
from fluent.syntax import parse, ast


def parse_ftl_to_dict(filepaths):
    """Парсит все .ftl файлы в папке и возвращает словарь {ключ: значение}."""
    translations = {}
    for filepath in filepaths:
        if filepath.endswith(".ftl"):
            with open(filepath, "r", encoding="utf-8") as f:
                resource = parse(f.read())
                for entry in resource.body:
                    # Нас интересуют только сообщения (Message), а не комментарии
                    if isinstance(entry, ast.Message):
                        key = entry.id.name
                        # Извлекаем текст (упрощенно, без учета сложной логики селекторов)
                        if entry.value:
                            # Собираем текстовые элементы сообщения
                            value = "".join([
                                element.value if hasattr(element, 'value') else "{var}"
                                for element in entry.value.elements
                            ])
                            if key not in translations:
                                translations[key] = value
                            else:
                                if value != translations[key]:
                                    new_key = f'{key}_1'
                                    assert new_key not in translations
                                    translations[new_key] = value
    return translations


def main():
    data_dir = '/home/adeshkin/khakas_projects/data/translation/common_voice/common-voice-main_web_locales/common-voice'
    lang2path = {
        'Русский': f'{data_dir}/ru',
        'Тувинский': f'{data_dir}/tyv',
        'Башкирский': f'{data_dir}/ba',
        'Киргизский': f'{data_dir}/ky',
        'Казахский': f'{data_dir}/kk',
    }

    data = {}
    for lang, folder_path in lang2path.items():
        modals_paths = glob.glob(f'{folder_path}/modals/*.ftl')
        pages_paths = glob.glob(f'{folder_path}/pages/*.ftl')
        contribute_paths = glob.glob(f'{folder_path}/pages/contribute/*.ftl')
        profile_paths = glob.glob(f'{folder_path}/pages/profile/*.ftl')
        all_paths = modals_paths + pages_paths + contribute_paths + profile_paths
        # assert len(all_paths) == 24, f"{lang} {len(all_paths)}"
        data[lang] = parse_ftl_to_dict(sorted(all_paths))

    df = pd.DataFrame(data)
    df.to_csv("/home/adeshkin/khakas_projects/data/translation/common_voice/common-voice_ru_tyv_ba_ky_kk.csv")


def main1():
    data_dir = '/home/adeshkin/khakas_projects/data/translation/common_voice/common-voice-main_web_locales/spontaneous-speech'
    lang2path = {
        'Русский': f'{data_dir}/ru',
        'Тувинский': f'{data_dir}/tyv',
        'Башкирский': f'{data_dir}/ba',
        'Киргизский': f'{data_dir}/ky',
        'Казахский': f'{data_dir}/kk',
    }

    data = {}
    for lang, folder_path in lang2path.items():
        modals_paths = glob.glob(f'{folder_path}/modals/*.ftl')
        pages_paths = glob.glob(f'{folder_path}/pages/*.ftl')
        contribute_paths = glob.glob(f'{folder_path}/pages/contribution/*.ftl')
        all_paths = modals_paths + pages_paths + contribute_paths
        # assert len(all_paths) == 24, f"{lang} {len(all_paths)}"
        data[lang] = parse_ftl_to_dict(sorted(all_paths))

    df = pd.DataFrame(data)
    df.to_csv("/home/adeshkin/khakas_projects/data/translation/common_voice/spontaneous-speech_ru_tyv_ba_ky_kk.csv")


def prepare_for_kjh_translate():
    path = "/home/adeshkin/Downloads/Абумова Ольга Дмитриевна - 2026 - spont_common_voice (1).csv"
    df = pd.read_csv(path)
    # df = df.drop_duplicates('Русский')
    print(df['Русский'][df['Русский'].duplicated()])
    sorted_df = df.sort_values(by='Русский', key=lambda x: x.str.len())
    sorted_df.to_csv(path.replace('.csv', '- sorted.csv'), index=False)


if __name__ == '__main__':
    prepare_for_kjh_translate()
