import discord
from discord.ext import commands, tasks
import sqlite3
import requests
from datetime import datetime
from config import TOKEN, NOTIFY_CHANNEL_ID
from steam_api import (
    extract_appid,
    get_game_name,
    get_release_date,
    get_price,
    price_to_number,
)
from database import (
    init_database,
    add_game,
    get_games,
    remove_game,
    update_price,
    is_url_registered,
    get_games_for_check,
    get_games_for_release_check,
    mark_release_notified,
    mark_released_notified,
    update_release_date,
)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def parse_japanese_date(date_text):
    try:
        return datetime.strptime(date_text, "%Y年%m月%d日").date()
    except ValueError:
        return None



#  ログインしたら価格チェックとリリース日チェックをするよ
#  データベースがなかったら作るよ

@bot.event
async def on_ready():
    init_database()
    print(f"ログイン成功: {bot.user}")

    if not auto_check_prices.is_running():
        auto_check_prices.start()

    if not auto_check_releases.is_running():
        auto_check_releases.start()


#  pingするとpong!してくれる

@bot.command()
async def ping(ctx):
    await ctx.send("pong!")



#  ゲームをリストに追加する


# @bot.command()
# async def add(ctx, *, game_name):
#    add_game(game_name)
#    await ctx.send(f"『{game_name}』を登録しました！")



 #  URLをリストに追加する

@bot.command()
async def watch(ctx, url):
    appid = extract_appid(url)

    if appid is None:
        await ctx.send("SteamのゲームURLを入力してください")
        return

    if is_url_registered(url):
        await ctx.send("このSteam URLはすでに登録されています")
        return

    game_name = get_game_name(appid)
    release_date = get_release_date(appid)
    price = get_price(appid)

    add_game(
         game_name,
         url,
         release_date,
         price
)

    await ctx.send(
        f"『{game_name}』を登録しました！\n"
        f"発売日: {release_date}"
    )


#  登録されたゲームのリストを表示する

@bot.command()
async def list(ctx):
    games = get_games()

    if not games:
        await ctx.send("登録されたゲームはありません")
        return

    message = "登録ゲーム一覧\n"

    for game_id, game_name, game_url, release_date, price in games:
       message += (
         f"ID: {game_id}\n"
         f"名前: {game_name}\n"
         f"発売日: {release_date}\n"
         f"価格: {price}\n"
         f"URL: {game_url}\n\n"
)

    await ctx.send(message)



#  登録されたゲームを削除する

@bot.command()
async def remove(ctx, game_id: int):
    removed_game = remove_game(game_id)

    if removed_game is None:
        await ctx.send("その番号は存在しません")
        return

    await ctx.send(f"『{removed_game}』を削除しました！")



#   金額をチェックする

@bot.command()
async def check(ctx):
    games = get_games_for_check()

    if not games:
        await ctx.send("監視中のゲームはありません")
        return

    for game_id, game_name, game_url, old_price in games:
        appid = extract_appid(game_url)

        if appid is None:
            await ctx.send(f"『{game_name}』のURLからAppIDを取得できませんでした")
            continue

        new_price = get_price(appid)

        await ctx.send(
            f"『{game_name}』を確認しました\n"
            f"保存価格: {old_price}\n"
            f"現在価格: {new_price}"
        )

        if old_price != new_price:
            await ctx.send(
                f"価格が変わりました！\n"
                f"『{game_name}』\n"
                f"以前: {old_price}\n"
                f"現在: {new_price}\n"
                f"{game_url}"
            )

            update_price(game_id, new_price)

    await ctx.send("価格チェック完了！")


#   自動で金額チェックするよ

@tasks.loop(hours=12)
async def auto_check_prices():
    print("自動価格チェックを実行しました")

    channel = bot.get_channel(NOTIFY_CHANNEL_ID)

    if channel is None:
        print("通知チャンネルが見つかりません")
        return

    games = get_games_for_check()

    for game_id, game_name, game_url, old_price in games:
        appid = extract_appid(game_url)

        if appid is None:
            continue

        new_price = get_price(appid)

        old_number = price_to_number(old_price)
        new_number = price_to_number(new_price)

        if old_number is not None and new_number is not None and new_number < old_number:
            discount_rate = round((old_number - new_number) / old_number * 100)

            await channel.send(
                f"🎉 Steamセール開始！\n\n"
                f"🎮 『{game_name}』\n"
                f"💰 {old_price} → {new_price}\n"
                f"🔥 約{discount_rate}%OFF\n\n"
                f"{game_url}"
            )

        update_price(game_id, new_price)


#   手動で7日後にリリースされるゲームを調べるよ

@bot.command()
async def releasecheck(ctx):
    games = get_games_for_release_check()

    if not games:
        await ctx.send("登録されたゲームはありません")
        return

    today = datetime.now().date()
    found = False

    for game_id, game_name, game_url, release_date in games:
        release_day = parse_japanese_date(release_date)

        if release_day is None:
            continue

        days_left = (release_day - today).days

        if days_left == 7:
            found = True
            await ctx.send(
                f"📅 発売7日前通知！\n\n"
                f"🎮 『{game_name}』\n"
                f"発売日: {release_date}\n"
                f"あと7日で発売です！\n\n"
                f"{game_url}"
            )

    if not found:
        await ctx.send("発売7日前のゲームはありませんでした")


#   自動で7日後にリリースされるゲームを調べて通知するよ

@tasks.loop(hours=12)
async def auto_check_releases():
    channel = bot.get_channel(NOTIFY_CHANNEL_ID)

    if channel is None:
        print("通知チャンネルが見つかりません")
        return

    games = get_games_for_release_check()
    today = datetime.now().date()

    for game_id, game_name, game_url, release_date, release_notified, released_notified in games:
        appid = extract_appid(game_url)

        if appid is None:
            continue

        new_release_date = get_release_date(appid)

        if release_date != new_release_date:
            old_release_day = parse_japanese_date(release_date)
            new_release_day = parse_japanese_date(new_release_date)

            if old_release_day is None and new_release_day is not None:
                await channel.send(
                    f"📢 発売日が決定しました！\n\n"
                    f"🎮 『{game_name}』\n"
                    f"発売日: {new_release_date}\n\n"
                    f"{game_url}"
                )

            update_release_date(game_id, new_release_date)
            release_date = new_release_date

        release_day = parse_japanese_date(release_date)

        if release_day is None:
            continue

        days_left = (release_day - today).days

        if days_left == 7 and release_notified == 0:
            await channel.send(
                f"📅 発売7日前通知！\n\n"
                f"🎮 『{game_name}』\n"
                f"発売日: {release_date}\n"
                f"あと7日で発売です！\n\n"
                f"{game_url}"
            )

            mark_release_notified(game_id)

        if days_left == 0 and released_notified == 0:
            await channel.send(
                f"🎉 本日発売！\n\n"
                f"🎮 『{game_name}』\n"
                f"発売日: {release_date}\n"
                f"ついに発売開始です！\n\n"
                f"{game_url}"
            )

            mark_released_notified(game_id)


bot.run(TOKEN)