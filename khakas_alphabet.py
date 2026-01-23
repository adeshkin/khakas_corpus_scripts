import unicodedata


for symbol in 'абвгдежзийклмнопрстуфхцчшщъыьэюяёіғңҷӧӱ':
    print(repr(symbol), unicodedata.name(symbol))