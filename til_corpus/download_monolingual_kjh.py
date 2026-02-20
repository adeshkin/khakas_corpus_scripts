# https://github.com/turkic-interlingua/til-mt/blob/7d988cc47dba889d02262d893bf9a46e43a6bb36/til_corpus/download_monolingual.py

import os

base_url = "gs://til-corpus/mono"

# all the langs present in the corpus
langs = ['alt', 'az', 'ba', 'cjs', 'crh', 'cv', 'gag', 'kaa', 'kjh', 'kk', 'krc', 'kum', 'ky', 'sah', 'slr', 'tk', 'tr',
         'tt', 'tyv', 'ug', 'uum', 'uz', 'en', 'ru']


# downloads a zip file given a url
def download_url(url, save_path):
    os.system(f"gsutil -m cp -r {url} {save_path}")


if __name__ == "__main__":
    language = 'kjh'
    assert language in langs

    download_url(f"{base_url}/{language}.txt",
                 f"/home/adeshkin/khakas_projects/data/translation/til_corpus/mono/{language}.txt")
