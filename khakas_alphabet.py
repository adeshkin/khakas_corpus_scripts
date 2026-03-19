import unicodedata

alphabet = 'абвгдежзийклмнопрстуфхцчшщъыьэюяёіғңҷӧӱ'
letters1 = 'а б в г ғ д е ё ж з и і й к л м н ң о ӧ п р с т у ӱ ф х ц ч ҷ ш щ ъ ы ь э ю я'.split()
# alphabet = sorted(alphabet)
# letters = sorted(letters1.copy())
# print(len(alphabet))
# print(len(letters))
#
# for symbol, letter in zip(alphabet, letters):
#     assert symbol == letter
#     print(repr(symbol), unicodedata.name(symbol))
print('\n\n')
print(letters1)
for letter in letters1:
    print(repr(letter), unicodedata.name(letter))

