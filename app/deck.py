"""«Колода» вопросов: весь список раздела перемешивается и проходится по порядку.

Состояние колоды (порядок + текущая позиция) хранится в сессии браузера —
подписанная cookie, отдельный стор не нужен. Вопросы выдаются без повторов,
пока колода не пройдена целиком; тогда она перемешивается заново.

При изменении файла-источника (version = mtime + размер) колода пересобирается,
а прогресс сбрасывается — это и есть «перемешивание при обновлении файла».
"""
import random

from flask import session

_SESSION_KEY = 'decks'


def advance(items: list[dict], version: str, key: str, delta: int) -> dict | None:
    """Сдвиг по колоде: delta=+1 — следующий вопрос, delta=-1 — назад.

    Возвращает {'item': ..., 'position': ...} или None для пустого списка.
    position (0 — первый вопрос) нужен фронту, чтобы прятать кнопку «назад»
    в начале колоды. «Назад» на первом вопросе остаётся на нём же.
    """
    n = len(items)
    if n == 0:
        return None

    decks = session.get(_SESSION_KEY) or {}
    deck = decks.get(key)
    if not deck or deck.get('version') != version or len(deck.get('order', [])) != n:
        deck = _new_deck(version, n)          # новый источник (или первый заход)
    else:
        pos = deck['position'] + delta
        if pos >= n:
            deck = _new_deck(version, n)      # колода пройдена — новый круг
        else:
            deck['position'] = max(pos, 0)

    decks[key] = deck
    session[_SESSION_KEY] = decks
    session.modified = True
    return {'item': items[deck['order'][deck['position']]], 'position': deck['position']}


def _new_deck(version: str, n: int) -> dict:
    order = list(range(n))
    random.shuffle(order)
    return {'version': version, 'order': order, 'position': 0}
