# based on https://github.com/adeshkin/onering_plugins_chrome_dev

"""Перевод колонки `ru` из CSV на хакасский (kjh) через translate.yandex.com.

Перевод делается не через API, а через живую вкладку Chromium, запущенного
с включённым remote debugging (CDP): в поле ввода подставляется русский текст,
из блока с переводом читается результат.

Запуск (см. README.md):
    chromium --remote-debugging-port=9222 --user-data-dir=/tmp/chromium-yandex
    python yandex_translate_csv_ru_kjh.py data.csv -o data_kjh.csv
"""

import argparse
import json
import os
import time

import pandas as pd
import requests
from websocket import create_connection

SRC_LANG = "ru"
TGT_LANG = "kjh"

INPUT_SELECTOR = "#fakeArea"
OUTPUT_SELECTOR = "#translation > span"

_id = 0


def connect(websocket_url):
    """Подключиться к вкладке по CDP.

    suppress_origin=True — Chrome/Chromium 111+ отклоняет WebSocket-рукопожатие
    с заголовком Origin (403 Forbidden), если браузер не запущен с
    --remote-allow-origins. Проще не отправлять Origin вовсе.
    """
    return create_connection(websocket_url, suppress_origin=True)


def send_request(websocket, method, params):
    """Отправить CDP-команду в открытую вкладку и вернуть result."""
    global _id
    _id += 1
    websocket.send(json.dumps({"id": _id, "method": method, "params": params}))
    res = json.loads(websocket.recv())
    if "error" in res:
        raise RuntimeError(res["error"])
    return res["result"]


def evaluate(websocket, expression):
    """Выполнить JS во вкладке и вернуть значение."""
    res = send_request(
        websocket,
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True},
    )
    return res["result"].get("value")


def create_target(port, fr_lang, to_lang):
    """Найти уже открытую вкладку переводчика или открыть новую, вернуть ws-url."""
    url = "https://translate.yandex.com/?source_lang={}&target_lang={}".format(fr_lang, to_lang)
    infos = requests.get("http://127.0.0.1:{}/json/list".format(port)).json()
    if not infos:
        raise RuntimeError("Нет открытых вкладок в браузере на порту {}".format(port))

    for info in infos:
        if info.get("url", "").startswith(url):
            return info["webSocketDebuggerUrl"]

    websocket = connect(infos[0]["webSocketDebuggerUrl"])
    target = send_request(websocket, "Target.createTarget", {"url": url})
    websocket.close()
    return "ws://127.0.0.1:{}/devtools/page/{}".format(port, target["targetId"])


def wait_load(websocket, timeout=60.0):
    """Дождаться загрузки страницы."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if evaluate(websocket, "document.readyState") == "complete":
            return True
        time.sleep(0.1)
    return False


def wait_translation(websocket, timeout=30.0, stable_for=0.6):
    """Дождаться непустого перевода и его стабилизации (Yandex дописывает текст)."""
    deadline = time.time() + timeout
    last, last_change = "", None
    while time.time() < deadline:
        value = evaluate(
            websocket,
            'var e = document.querySelector("{}"); e ? e.innerText : ""'.format(OUTPUT_SELECTOR),
        ) or ""
        if value != last:
            last, last_change = value, time.time()
        elif value and time.time() - last_change >= stable_for:
            return value
        time.sleep(0.1)
    return last


def translate(websocket, text):
    """Вставить текст в поле ввода и вернуть перевод."""
    evaluate(
        websocket,
        'var e = document.querySelector("{}"); if (e) e.innerText = "";'.format(OUTPUT_SELECTOR),
    )
    evaluate(
        websocket,
        "var i = document.querySelector({sel}); i.innerText = {text}; "
        'i.dispatchEvent(new Event("input", {{bubbles: true, cancelable: true}}));'.format(
            sel=json.dumps(INPUT_SELECTOR), text=json.dumps(text)
        ),
    )
    wait_load(websocket)
    return wait_translation(websocket)


def translate_with_retries(websocket_url, text, retries=3, pause=2.0):
    """Перевод с переподключением к вкладке при ошибках/пустом ответе."""
    for attempt in range(retries):
        try:
            websocket = connect(websocket_url)
            try:
                res = translate(websocket, text)
            finally:
                websocket.close()
            if res:
                return res
        except Exception as e:  # обрыв ws, зависшая вкладка и т.п.
            print("  ошибка (попытка {}/{}): {}".format(attempt + 1, retries, e))
        time.sleep(pause)
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Перевод колонки 'ru' из CSV на хакасский (kjh) через Yandex Translate в Chromium."
    )
    parser.add_argument("input_csv", help="путь к входному CSV с колонкой 'ru'")
    parser.add_argument("-o", "--output", help="путь к выходному CSV (по умолчанию <input>_kjh.csv)")
    parser.add_argument("-c", "--column", default="ru", help="имя колонки с русским текстом (по умолчанию 'ru')")
    parser.add_argument("--port", default="9222", help="порт remote debugging Chromium (по умолчанию 9222)")
    parser.add_argument("--sleep", type=float, default=0.5, help="пауза между запросами, сек (по умолчанию 0.5)")
    parser.add_argument("--limit", type=int, help="перевести только первые N строк")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="продолжить: пропустить строки, уже переведённые в выходном файле",
    )
    args = parser.parse_args()

    output_csv = args.output or os.path.splitext(args.input_csv)[0] + "_kjh.csv"

    df = pd.read_csv(args.input_csv)
    if args.column not in df.columns:
        raise SystemExit(
            "В файле нет колонки '{}'. Есть: {}".format(args.column, ", ".join(df.columns))
        )
    if args.limit:
        df = df.head(args.limit)

    done = 0
    if args.resume and os.path.exists(output_csv):
        done = len(pd.read_csv(output_csv))
        print("Продолжаем: уже переведено {} строк".format(done))

    websocket_url = create_target(args.port, SRC_LANG, TGT_LANG)
    print("Вкладка переводчика:", websocket_url)

    websocket = connect(websocket_url)
    wait_load(websocket)
    websocket.close()

    rows = df.to_dict("records")
    total = len(rows)
    for i, row in enumerate(rows):
        if i < done:
            continue
        text = row[args.column]
        text = "" if pd.isna(text) else str(text).strip()

        row[TGT_LANG] = translate_with_retries(websocket_url, text) if text else ""
        print("[{}/{}] {} -> {}".format(i + 1, total, text[:60], row[TGT_LANG][:60]))

        # пишем построчно, чтобы не потерять прогресс при сбое
        header = not os.path.exists(output_csv) or (i == 0 and not args.resume)
        pd.DataFrame([row]).to_csv(
            output_csv, mode="w" if header else "a", header=header, index=False
        )
        time.sleep(args.sleep)

    print("Готово:", output_csv)


if __name__ == "__main__":
    main()
