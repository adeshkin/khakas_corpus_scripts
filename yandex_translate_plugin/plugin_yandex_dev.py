# based on https://github.com/adeshkin/onering_plugins_chrome_dev

import json
import os
import time

import requests
from websocket import create_connection

modname = os.path.basename(__file__)[:-3]  # calculating modname



_next_request_id = 1


def send_cdp_request(websocket, method: str, params: dict) -> dict:
    global _next_request_id
    _next_request_id += 1
    websocket.send(json.dumps({"id": _next_request_id, "method": method, "params": params}))
    return json.loads(websocket.recv())["result"]


def evaluate_js(websocket, expression: str, return_by_value: bool = False) -> dict:
    return send_cdp_request(websocket, "Runtime.evaluate", {
        "expression": expression,
        "returnByValue": return_by_value,
    })


def wait_page_loaded(websocket, poll_interval: float = 0.1, max_attempts: int = 10000):
    for _ in range(max_attempts):
        state = evaluate_js(websocket, "document.readyState")
        if state["result"]["value"] == "complete":
            return
        time.sleep(poll_interval)


def wait_translation_result(websocket, poll_interval: float = 0.1, max_attempts: int = 10000) -> str:
    # Yandex fills #translation asynchronously, so poll until it's non-empty.
    for _ in range(max_attempts):
        state = evaluate_js(
            websocket,
            'document.querySelector("#translation > span").innerText',
            return_by_value=True,
        )
        value = state["result"].get("value")
        if value:
            return value
        time.sleep(poll_interval)
    return ""


def run_translation(websocket_url: str, content: str) -> str:
    websocket = create_connection(websocket_url)

    evaluate_js(websocket, 'document.querySelector("#translation > span").innerText=""')

    # json.dumps produces a safely-quoted JS string literal, so translated
    # text containing backticks/quotes can't break out of the expression.
    content_js_literal = json.dumps(content)
    fill_input_js = (
        'i=document.querySelector("#fakeArea");'
        'i.innerText={content};'
        'event = new Event("input", {{bubbles: true, cancelable: true}});'
        'i.dispatchEvent(event);'
    ).format(content=content_js_literal)
    evaluate_js(websocket, fill_input_js)

    wait_page_loaded(websocket)
    return wait_translation_result(websocket)


def find_or_create_translate_tab(port: str, from_lang: str, to_lang: str) -> str:
    target_url = "https://translate.yandex.com/?source_lang={}&target_lang={}".format(from_lang, to_lang)
    tabs = requests.get("http://127.0.0.1:{}/json/list".format(port)).json()

    for tab in tabs:
        if tab["url"].startswith(target_url):
            websocket_url = tab["webSocketDebuggerUrl"]
            break
    else:
        control_websocket = create_connection(tabs[0]["webSocketDebuggerUrl"])
        result = send_cdp_request(control_websocket, "Target.createTarget", {"url": target_url})
        websocket_url = "ws://127.0.0.1:{}/devtools/page/{}".format(port, result["targetId"])

    print("deb url:", websocket_url)
    return websocket_url


# --- Plugin API ---------------------------------------------------------

def init(core):
    core.yandex_dev_dict_websocketurl = {}

    port = core.plugin_options(modname).get("port")
    lang_pairs = core.plugin_options(modname).get("lang_pairs").split(",")

    for pair in lang_pairs:
        from_lang, to_lang = pair.split("->")
        core.yandex_dev_dict_websocketurl[pair] = find_or_create_translate_tab(port, from_lang, to_lang)


def translate(core, text: str, from_lang: str = "", to_lang: str = "", add_params: str = ""):
    websocket_url = core.yandex_dev_dict_websocketurl.get(f"{from_lang}->{to_lang}")
    return run_translation(websocket_url, text)


if __name__ == "__main__":
    class DummyCore:
        def plugin_options(self, mod):
            return {
                "port": "9222",
                "lang_pairs": "ru->kjh,kjh->ru",  # language pair to open in Yandex Translate
            }

    core = DummyCore()

    print("Инициализация вкладок в браузере...")
    init(core)  # Инициализируем соединение с Chrome и создаем вкладки

    print("Переводим...")
    result = translate(core, text="Вопрос: Опишите случай, когда вам пришлось принимать решение, не имея всех необходимых данных и информации.", from_lang="ru", to_lang="kjh")
    print("Итоговый перевод:", result)
