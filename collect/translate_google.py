import asyncio
from googletrans import Translator
import pandas as pd


async def translate_words(words):
    # Переводим список слов
    async with Translator() as translator:
        translations = await translator.translate(words, src='en', dest='ru')

    # Возвращаем словарь с исходными словами и их переводом
    return {word: translation.text for word, translation in zip(words, translations)}


df_en = pd.read_excel('/home/adeshkin/Desktop/gatitos/gatitos_english.xlsx', header=None)
words_to_translate = df_en[0].values.tolist()[:30]
result = asyncio.run(translate_words(words_to_translate))
print(result)
