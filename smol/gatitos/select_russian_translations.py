"""Выбор наиболее подходящих русских переводов для английских слов gatitos.

Вход: json с ответами Яндекс.Словаря (en-ru).
Выход: для каждого английского слова — отсортированный по убыванию релевантности
список русских слов (редкие отсеиваются). Эти слова затем переводятся на хакасский:
несколько вариантов нужны потому, что у конкретного русского слова хакасского
соответствия может не быть, а у его синонима — есть.
"""
import argparse
import json
import re
import statistics
from collections import Counter

import pandas as pd

DEFAULT_INPUT = '/home/adeshkin/Downloads/gatitos_yandex_dict_result_error_copy.json'

# штрафы к score
DEF_PENALTY = 0.5    # за порядковый номер части речи (def)
TR_PENALTY = 0.3     # за порядковый номер перевода внутри def
SYN_PENALTY = 0.4    # за порядковый номер синонима внутри перевода
MULTIWORD_PENALTY = 0.3


def normalize(text):
    """Форма для дедупликации: без регистра, ё -> е, лишние пробелы убраны."""
    return re.sub(r'\s+', ' ', text.strip().lower()).replace('ё', 'е')


def collect_candidates(entry):
    """Все русские кандидаты одного английского слова со скорингом."""
    candidates = []
    for def_idx, definition in enumerate(entry.get('def', [])):
        for tr_idx, tr in enumerate(definition.get('tr', [])):
            tr_fr = tr.get('fr', 1)
            items = [(tr, tr_fr, 0, False)]
            for syn_idx, syn in enumerate(tr.get('syn', []), 1):
                # синоним не может быть релевантнее своего головного перевода
                items.append((syn, min(syn.get('fr', 1), tr_fr), syn_idx, True))

            for item, fr, syn_idx, is_syn in items:
                text = item.get('text', '').strip()
                if not text:
                    continue
                n_words = len(text.split())
                score = (fr
                         - DEF_PENALTY * def_idx
                         - TR_PENALTY * tr_idx
                         - SYN_PENALTY * syn_idx
                         - MULTIWORD_PENALTY * (n_words > 1))
                candidates.append({
                    'ru': text,
                    'fr': fr,
                    'pos': item.get('pos') or definition.get('pos'),
                    'gen': item.get('gen'),
                    'asp': item.get('asp'),
                    'is_syn': is_syn,
                    'n_words': n_words,
                    'score': round(score, 3),
                })
    return candidates


def dedup(candidates):
    """Оставляем по одной форме на нормализованный вариант — с лучшим score."""
    best = {}
    for cand in candidates:
        key = normalize(cand['ru'])
        if key not in best or cand['score'] > best[key]['score']:
            best[key] = cand
    return list(best.values())


def select(candidates, min_fr, min_n, max_n, max_words, first_pos_only):
    if first_pos_only:
        candidates = [c for c in candidates if c['score'] > -DEF_PENALTY]
    if max_words:
        candidates = [c for c in candidates if c['n_words'] <= max_words]

    candidates = dedup(candidates)
    candidates.sort(key=lambda c: -c['score'])

    frequent = [c for c in candidates if c['fr'] >= min_fr]
    rare = [c for c in candidates if c['fr'] < min_fr]

    selected = frequent[:max_n]
    if len(selected) < min_n:  # добиваем редкими, чтобы слово не осталось пустым
        selected += rare[:min_n - len(selected)]
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', default=DEFAULT_INPUT)
    parser.add_argument('--out-json', default='gatitos_ru_candidates.json')
    parser.add_argument('--out-csv', default='gatitos_ru_candidates.csv')
    parser.add_argument('--out-missing', default='gatitos_no_translation.txt')
    parser.add_argument('--min-fr', type=int, default=5,
                        help='минимальная частота (fr) не-редкого перевода')
    parser.add_argument('--min-n', type=int, default=2)
    parser.add_argument('--max-n', type=int, default=5)
    parser.add_argument('--max-words', type=int, default=0,
                        help='максимум слов в переводе, 0 = без ограничения')
    parser.add_argument('--first-pos-only', action='store_true',
                        help='брать только первую часть речи (первый def)')
    args = parser.parse_args()

    with open(args.input, encoding='utf-8') as f:
        data = json.load(f)

    result = {}
    missing = []
    for word, entry in data.items():
        candidates = collect_candidates(entry)
        selected = select(candidates, args.min_fr, args.min_n, args.max_n,
                          args.max_words, args.first_pos_only)
        if not selected:
            missing.append(word)
            continue
        result[word] = selected

    with open(args.out_json, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    rows = []
    for word, selected in result.items():
        variants = [c['ru'] for c in selected]
        row = [word] + variants + [''] * (args.max_n - len(variants))
        row.append('; '.join(variants))
        rows.append(row)
    columns = ['en'] + [f'ru_{i}' for i in range(1, args.max_n + 1)] + ['ru_all']
    pd.DataFrame(rows, columns=columns).to_csv(args.out_csv, index=False)

    with open(args.out_missing, 'w', encoding='utf-8') as f:
        f.write('\n'.join(missing) + '\n')

    counts = [len(v) for v in result.values()]
    print(f'всего слов: {len(data)}, с переводом: {len(result)}, без перевода: {len(missing)}')
    print(f'вариантов на слово: среднее {statistics.mean(counts):.2f}, '
          f'медиана {statistics.median(counts)}, макс {max(counts)}')
    print('распределение:', sorted(Counter(counts).items()))
    print(f'\nсохранено: {args.out_json}, {args.out_csv}, {args.out_missing}')

    print('\nпримеры:')
    for word in list(result)[:15]:
        print(f'  {word}: ' + '; '.join(c['ru'] for c in result[word]))


if __name__ == '__main__':
    main()
