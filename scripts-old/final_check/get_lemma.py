import pymorphy3

# Initialize the analyzer (do this once, it loads a dictionary)
morph = pymorphy3.MorphAnalyzer(lang='ru')

# The word you want to lemmatize
word = "googleда"

# Parse the word
parsed_word = morph.parse(word)[0]

# Extract the lemma (normal form)
lemma = parsed_word.normal_form

print(f"Original: {word}")
print(f"Lemma: {repr(lemma)}")