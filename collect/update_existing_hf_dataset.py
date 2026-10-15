import argparse

from datasets import Dataset, concatenate_datasets, load_dataset

# parser = argparse.ArgumentParser(description='Анализ и обновление хакасско-русского корпуса')
# parser.add_argument('--push', action='store_true', help='Опубликовать объединённый датасет на Hugging Face')
# args = parser.parse_args()

REPOSITORY_ID = 'adeshkin/khakas-russian-parallel-corpus'

current_dataset = load_dataset(REPOSITORY_ID, split='train')

d = {'khakaschiry': ['газета "Хакас чирі"', 
                     '"Khakas Chiry" newspaper', 
                     'газетная статья', 
                     'newspaper article',
                     'https://www.khakaschiry.ru/', 
                     'khakas-chiry-newspaper'],
     'khakaschiry_akciya_lydi': ['газета "Хакас чирі"', 
                     '"Khakas Chiry" newspaper', 
                     'газетная статья', 
                     'newspaper article',
                     'https://www.khakaschiry.ru/', 
                     'khakas-chiry-newspaper'],
    'khakaschiry_akciya_nn': ['газета "Хакас чирі"', 
                         '"Khakas Chiry" newspaper', 
                         'газетная статья', 
                         'newspaper article',
                         'https://www.khakaschiry.ru/', 
                         'khakas-chiry-newspaper'],
     'uchebniki_fixed': ['Школьные учебники, научные статьи, литература', 
                         'School textbooks, scientific articles, literature', 
                         'образование', 
                         'education',
                         'none',
                         'khakas-materials'],
      'uchebniki': ['Школьные учебники, научные статьи, литература', 
                               'School textbooks, scientific articles, literature', 
                               'образование', 
                               'education',
                               'none',
                               'khakas-materials'],
        'shulbaeva choohtar': ['Шулбаева Чоохтар', 
                                       "Shulbayeva's stories", 
                                       'сборник рассказов и очерков',
                                       'collection of short stories and essays',
                                       'none',
                                       'khakas-materials'], 
         'my examples': ['Повседневные фразы', 
                                               "Everyday phrases", 
                                               'многодоменный',
                                               'multi-domain',
                                               'none',
                                               'russian-materials'],
        'spontaneous common voice interface': ['Интерфейс spontaneous common voice', 
                        "Spontaneous common voice interface", 
                        'технический',
                        'technical',
                        'none',
                        'russian-materials'],
        'common voice interface': ['Интерфейс common voice', 
                                "Common voice interface", 
                                'технический',
                                'technical',
                                'none',
                                'russian-materials'],
        'Trunova': ['Рассказы для детей', 
                    "Stories for children", 
                    'сборник рассказов и очерков',
                                                           'collection of short stories and essays',
                                                           'none',
                    'russian-materials'],
        'averoo_sumi_ru_alpaca': ['Промпт для нейросетей', 
            "Prompt for neural networks", 
            'многодоменный',
                                                            'multi-domain',
                                                            'none',
                                                            'russian-materials'], 
        'ru_alpaca': ['Промпт для нейросетей', 
            "Prompt for neural networks", 
            'многодоменный',
            'multi-domain',
            'none',
            'russian-materials'], 
        'gwmt': ['google/wmt24pp', 
                    "google/wmt24pp", 
                    'многодоменный',
                    'multi-domain',
                    'https://huggingface.co/datasets/google/wmt24pp',
                    'russian-materials'], 
        'coregrammar': ['Сложное предложение', 
                "Complex sentence", 
                'многодоменный',
                'multi-domain',
                'none',
                'russian-materials'], 
        
    }
import pandas as pd 

df1 = pd.read_csv("/home/adeshkin/Downloads/final_all_2026_fix_symbols_final.csv")

missing_sources = df1.loc[~df1['Полное название'].isin(d), 'Полное название'].unique()
if len(missing_sources):
    raise ValueError(f"Источники отсутствуют в d: {missing_sources.tolist()}")

metadata_columns = [
    'source_name_ru', 'source_name_en', 'domain_ru', 'domain_en',
    'source_url', 'source_id',
]
for i, column in enumerate(metadata_columns):
    df1[column] = df1['Полное название'].map(lambda source: d[source][i])

df1 = df1.rename(columns={
    'Русский': 'ru',
    'Хакасский': 'kjh',
    'Исходный язык': 'source_language',
})
df1['source_language'] = df1['source_language'].map({
    'Русский': 'ru',
    'Хакасский': 'kjh',
})
df = df1[current_dataset.column_names]


# for column in metadata_columns:
#     print(f"\n{column}:")
#     print(df[column].unique().tolist())


for column in df.columns:
    invalid = df[column].isna() | df[column].str.strip().eq('')
    if invalid.any():
        raise ValueError(f"Пустые значения в {column}: {int(invalid.sum())} строк")

new_rows_dataset = Dataset.from_pandas(
    df,
    features=current_dataset.features,
    preserve_index=False,
)
updated_dataset = concatenate_datasets([current_dataset, new_rows_dataset])
print(f"Старое количество строк: {len(current_dataset)}")
print(f"Новое количество строк: {len(updated_dataset)}")

updated_dataset.push_to_hub(
    repo_id=REPOSITORY_ID,
    split='train',
    token='',
    commit_message='Update Khakas-Russian parallel corpus with new translations',
)
print(f"Загружено {len(updated_dataset)} строк: https://huggingface.co/datasets/{REPOSITORY_ID}")
