import json
from glob import glob



def main():
    data_dir = '/home/adeshkin/Desktop/tolk_tom_1/part_2_22-95 (Copy)'
    paths = sorted(glob(f'{data_dir}/*/*.json'))
    all_data = {}
    for path in paths:
        with open(path) as json_file:
            data = json.load(json_file)

        for item in data:
            headword = item.pop('headword', None)
            assert headword is not None

            homonym_index = item.pop('homonym_index', None)
            if homonym_index is None:
                homonym_index = 'I'
            
            if headword not in all_data:
                all_data[headword] = {}
            all_data[headword][homonym_index] = item


    with open('all_data.json', 'w') as json_file:
        json.dump(all_data, json_file, ensure_ascii=False, indent=4)
        

if __name__ == '__main__':
    main()
