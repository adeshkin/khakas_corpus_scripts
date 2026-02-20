# https://github.com/turkic-interlingua/til-mt/blob/7d988cc47dba889d02262d893bf9a46e43a6bb36/til_corpus/download_data.py

import os

base_url = "gs://til-corpus/corpus"

# all the langs present in the corpus
langs = ['alt', 'az', 'ba', 'cjs', 'crh', 'cv', 'gag', 'kaa', 'kjh', 'kk', 'krc', 'kum', 'ky', 'sah', 'slr', 'tk', 'tr',
         'tt', 'tyv', 'ug', 'uum', 'uz', 'en', 'ru']


# downloads a zip file given a url
def download_url(url, save_path):
    os.system(f"gsutil -m cp -r {url} {save_path}")


if __name__ == "__main__":
    splits = ["train", "dev", "test"]
    source = 'kjh'
    target = 'ru'

    for split in splits:
        save_path = f"/home/adeshkin/khakas_projects/data/translation/til_corpus/para/{split}"
        os.makedirs(save_path, exist_ok=False)
        download_path = f"{base_url}/{split}/{source}-{target}"
        print(f"Downloading {split} files...")
        download_url(download_path, save_path)
