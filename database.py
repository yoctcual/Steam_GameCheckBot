import sqlite3


 #　データを取得

def add_game(name, url, release_date, price):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO games (name, url, release_date, price) VALUES (?, ?, ?, ?)",
    (name, url, release_date, price)
    )

    conn.commit()
    conn.close()


def get_games():
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT id, name, url, release_date, price FROM games"
    )

    games = cursor.fetchall()

    conn.close()

    return games


def remove_game(game_id):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM games WHERE id = ?",
        (game_id,)
    )

    result = cursor.fetchone()

    if result is None:
        conn.close()
        return None

    game_name = result[0]

    cursor.execute(
        "DELETE FROM games WHERE id = ?",
        (game_id,)
    )

    conn.commit()
    conn.close()

    return game_name


def update_price(game_id, new_price):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE games SET price = ? WHERE id = ?",
        (new_price, game_id)
    )

    conn.commit()
    conn.close()


def is_url_registered(url):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM games WHERE url = ?",
        (url,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def get_games_for_check():
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, url, price FROM games"
    )

    games = cursor.fetchall()

    conn.close()

    return games


def get_games_for_release_check():
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, url, release_date, release_notified, released_notified FROM games"
    )

    games = cursor.fetchall()

    conn.close()

    return games


def mark_release_notified(game_id):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE games SET release_notified = 1 WHERE id = ?",
        (game_id,)
    )

    conn.commit()
    conn.close()


def mark_released_notified(game_id):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE games SET released_notified = 1 WHERE id = ?",
        (game_id,)
    )

    conn.commit()
    conn.close()


def update_release_date(game_id, new_release_date):
    conn = sqlite3.connect("games.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE games SET release_date = ? WHERE id = ?",
        (new_release_date, game_id)
    )

    conn.commit()
    conn.close()