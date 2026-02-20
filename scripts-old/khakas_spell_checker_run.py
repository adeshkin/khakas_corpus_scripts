from spellchecker import SpellChecker

my_dictionary_path = '/home/adeshkin/Desktop/defis_words/my_custom_kjh_uchebniki.json.gz'

# 1. Инициализируем SpellChecker, НЕ указывая язык (language=None)
# 2. Указываем путь к нашему словарю
spell = SpellChecker(language=None, local_dictionary=my_dictionary_path, distance=5)

# Теперь он работает с вашим словарем!
words_to_check = ['нимен!', 'улуг', 'мыҷырмаҷыр', 'к!з!н!н', 'полгам!']
misspelled = spell.unknown(words_to_check)

for word in misspelled:
    print(f"Исправление для {word}: {spell.correction(word)}")
    print(f'{spell.candidates(word)}')

print()
print('-'*20)
print()

spell.distance = 1

misspelled = spell.unknown(words_to_check)

for word in misspelled:
    print(f"Исправление для {word}: {spell.correction(word)}")
    print(f'{spell.candidates(word)}')