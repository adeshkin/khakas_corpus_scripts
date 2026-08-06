import pandas as pd
import re

def download_hf_dataset():
    df1 = pd.read_parquet("hf://datasets/adeshkin/khakas-towns-villages/data/train-00000-of-00001.parquet")
    df1.to_csv('/home/adeshkin/Downloads/khakas-towns-villages.csv', index=False)
    df = pd.read_parquet("hf://datasets/adeshkin/khakas-russian-parallel-corpus/data/train-00000-of-00001.parquet")
    df.to_csv('/home/adeshkin/Downloads/khakas-russian-parallel-corpus.csv', index=False)


def get_geo_names(x, ru_objects, ru_kjh_map):
    objects = []
    for ru_object in ru_objects:
        pattern = r'\b' + re.escape(ru_object)# + r'\b'
        if re.search(pattern, x):
            objects.append(ru_object)

    text1 = [f'{ru_kjh_map[obj][0]}    ->    {ru_kjh_map[obj][1]}' for obj in objects]
    text = '\n'.join(text1)

    return text if len(objects) > 0 else ''


def main():
    df1 = pd.read_csv('/home/adeshkin/Downloads/khakas-towns-villages.csv')
    print(len(df1))
    df1 = df1[df1['ru_short'] != df1['kjh_short']]
    ru_kjh_list = df1[['ru_short', 'kjh_short', 'ru', 'kjh']].values.tolist()
    ru_kjh_map = {}

    for ru_name, kjh_name, ru_item, kjh_item in ru_kjh_list:
        ru_kjh_map[ru_name] = (ru_item, kjh_item)
    ru_kjh_map['Алтай район'] = ('Алтай район', 'Алтай аймаа')
    ru_kjh_map['Асхыс район'] = ('Асхыс район', 'Асхыс аймаа')
    ru_kjh_map['Пии район'] = ('Пии район', 'Пии аймаа')
    ru_kjh_map['Орджоникидзе район'] = ('Орджоникидзе район', 'Орджоникидзе аймаа')
    ru_kjh_map['Ағбан пилтірі район'] = ('Ағбан пилтірі район', 'Ағбан пилтірі аймаа')
    ru_kjh_map['Усть-Абакан район'] = ('Усть-Абакан район', 'Ағбан пилтірі аймаа')
    ru_kjh_map['Боград район'] = ('Боград район', 'Боград аймаа')
    ru_kjh_map['Тастып район'] = ('Тастып район', 'Тастып аймаа')
    ru_kjh_map['Таштып район'] = ('Таштып район', 'Тастып аймаа')
    ru_kjh_map['Сыра район'] = ('Сыра район', 'Сыра аймаа')
    ru_kjh_map['Шира район'] = ('Шира район', 'Сыра аймаа')
    ru_objects = list(ru_kjh_map.keys())

    df = pd.read_csv('/home/adeshkin/Downloads/khakas-russian-parallel-corpus.csv')
    df['ru_object'] = df['kjh'].apply(lambda x: get_geo_names(x, ru_objects, ru_kjh_map))
    # print(df['ru_object'])
    df[df['ru_object'] != ''].to_csv('/home/adeshkin/Downloads/khakas-russian-parallel-to-check.csv')


if __name__ == '__main__':
    main()


