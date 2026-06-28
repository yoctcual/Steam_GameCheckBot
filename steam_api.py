import requests


#   STEAMAPI周りの読み込みはここだよ

def extract_appid(url):
    parts = url.split("/")

    if "app" not in parts:
        return None

    app_index = parts.index("app")

    if app_index + 1 >= len(parts):
        return None

    return parts[app_index + 1]


def get_game_name(appid):
    url = (
        f"https://store.steampowered.com/api/appdetails"
        f"?appids={appid}&cc=jp&l=japanese"
    )

    response = requests.get(url)
    data = response.json()

    return data[str(appid)]["data"]["name"]


def get_release_date(appid):
    url = (
        f"https://store.steampowered.com/api/appdetails"
        f"?appids={appid}&cc=jp&l=japanese"
    )

    response = requests.get(url)
    data = response.json()

    return data[str(appid)]["data"]["release_date"]["date"]


def get_price(appid):
    url = (
        f"https://store.steampowered.com/api/appdetails"
        f"?appids={appid}&cc=jp&l=japanese"
    )

    response = requests.get(url)
    data = response.json()

    game_data = data[str(appid)]["data"]

    if "price_overview" not in game_data:
        return "価格情報なし"

    return game_data["price_overview"]["final_formatted"]


def price_to_number(price):
    if price is None:
        return None

    if price == "価格情報なし":
        return None

    price = price.replace("¥", "")
    price = price.replace(",", "")
    price = price.strip()

    if not price.isdigit():
        return None

    return int(price)