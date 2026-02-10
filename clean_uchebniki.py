from glob import glob
import re


def find_valid_enumeration(text_to_check, min_items=4, max_words=2):
    """
    Проверяет, есть ли в тексте подряд идущее перечисление (min_items)
    элементов, где каждый элемент состоит не более чем из (max_words) слов.
    """

    # 1. Разбиваем весь текст на элементы по запятой
    # .strip() убирает лишние пробелы по краям (напр. " яблоко ")
    items = [item.strip() for item in text_to_check.split(',')]

    consecutive_valid_count = 0

    # 2. Проходим по каждому элементу
    for item in items:
        # 3. Считаем слова в элементе.
        # .split() по умолчанию делит по пробелам
        words = item.split()
        word_count = len(words)

        # 4. Проверяем условие
        # Элемент валиден, если в нем есть слова (не пустой)
        # и слов не больше, чем max_words
        if 0 < word_count <= max_words:
            # Если элемент подходит, увеличиваем счетчик
            consecutive_valid_count += 1
        else:
            # Если элемент не подходит (например, 3 слова или пустой),
            # сбрасываем счетчик подряд идущих
            consecutive_valid_count = 0

        # 5. Проверяем, не достигли ли мы цели
        if consecutive_valid_count >= min_items:
            # Нашли 3 (или больше) подряд!
            return True

    # 6. Если прошли весь список и не нашли, возвращаем False
    return False

def has_spaced_chars(text):
    # Check for patterns like "п р и л а г а т е л ь н а й" (words with spaces between chars)
    return bool(re.search(r'\b(?:[А-Яа-яЁёІіҒғҢңҶҷӦӧӰӱ] ){3,}\b', text.lower()))


def clean_text(text):
    # Remove patterns like (А. Тюкпеев) or (Б. Дав.)
    text = re.sub(r'\([А-ЯЁІіҒғҢңҶҷӦӧӰӱ]+\.\s*[А-Яа-яЁёІіҒғҢңҶҷӦӧӰӱ\s]+\.?\)', '', text)
    # Remove patterns like (К. Д. У ш и н с к и й)
    text = re.sub(r'\([А-ЯЁІіҒғҢңҶҷӦӧӰӱ]+\.\s*[А-ЯЁІіҒғҢңҶҷӦӧӰӱ]+\.\s*[А-Яа-яЁёІіҒғҢңҶҷӦӧӰӱ\s]+\.?\)', '', text)

    # Remove words with spaces between characters like "Ы з ы р ғ а." or "Х о р х л о."
    text = re.sub(r'\b(?:[А-Яа-яЁёІіҒғҢңҶҷӦӧӰӱ]\s){2,}[А-Яа-яЁёІіҒғҢңҶҷӦӧӰӱ]\b\.', '', text)

    return text


def main():
    data_dir = '/home/adeshkin/Desktop/uchebniki_docx'
    paths = sorted(glob(f'{data_dir}/*/*.txt'))
    for path in paths:
        if '_cl' in path:
            continue
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = ['# СТРОКИ ДЛЯ ПЕРЕВОДА НАЧАЛО\n']
        for line in lines:
            line = clean_text(line)
            line = line.replace('Ноға?', ' ')
            line = re.sub(r'\bп\b.', ' ', line)
            line = line.strip()

            if bool(re.search(r'\bан\b.', line)):
                if not bool(re.search(r'\bан\b. п.', line)) and not bool(re.search(r'\bан\b. пасх.', line)):
                    line = re.sub(r'\bан\b.', 'ан. п.', line)

            if has_spaced_chars(line):
                continue

            if not bool(re.search(r'[ІіҒғҢңҶҷӦӧӰӱ]', line)):
                continue

            if find_valid_enumeration(line):
                continue

            if '(' in line or ')' in line:
                continue

            if '…' in line or '...' in line:
                continue

            if 'текст' in line.lower():
                continue

            if ('пазыңар' in line.lower()
                    or 'пиріңер' in line.lower() or 'чарыңар' in line.lower()
                    or 'пӱдіріңер' in line.lower() or 'пас салыңар' in line.lower()
                    or 'чарыдыңар' in line.lower() or 'пазып алыңар' in line.lower()
                    or 'ӱзӱріңер' in line.lower() or 'Сағын салыңар'.lower() in line.lower()
                    or 'тиңнестіріңер' in line.lower()):
                continue

            # if 'ңар' in line or 'ңер' in line:
            #     if 'наңар' in line or 'неңер' in line or 'даңар' in line or 'деңер' in line or 'аннаңар' in line.lower():
            #         print(0)
            #     else:
            #         print(line)
            #         continue



            cleaned_lines.append(f'{line}\n')
        cleaned_lines.append('# СТРОКИ ДЛЯ ПЕРЕВОДА КОНЕЦ')
        with open(path.replace('.txt', '_cl.txt'), 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)


if __name__ == "__main__":
    main()
