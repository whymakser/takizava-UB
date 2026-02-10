import os, sys, importlib, asyncio, re, subprocess, secrets, time
from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher, types as aiotypes
from aiogram.client.default import DefaultBotProperties
from forelka.kernel import Kernel
from forelka.auth import Authenticator

C, G, Y, R, W = "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[0m"

bot_kernel = Kernel()

def banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    art = f"""{C}  __               _ _         
 / _|             | | |        
| |_ ___  _ __ ___| | | ____ _ 
|  _/ _ \\| '__/ _ \\ | |/ / _` |
| || (_) | | |  __/ |   < (_| |
|_| \\___/|_|  \\___|_|_|\\_\\__,_|{W}"""
    print(art)
    print(f"{G}Forelka starting.. | Commit: #{bot_kernel.get_commit()}{W}\n")

async def auto_setup(client):
    if not bot_kernel.config.get("bot_token"):
        h = secrets.token_hex(4)
        async with client.conversation("@BotFather") as conv:
            await conv.send_message("/newbot")
            await conv.get_response()
            await conv.send_message(f"Forelka {h}")
            await conv.get_response()
            await conv.send_message(f"f_{h}_bot")
            res = await conv.get_response()
            token = re.search(r"(\d+:[A-Za-z0-9_-]+)", res.text)
            if token:
                bot_kernel.config["bot_token"] = token.group(1)
                bot_kernel.save_config()

async def main():
    banner()
    
    if not bot_kernel.config.get("api_id"):
        bot_kernel.config["api_id"] = int(input(f"{G}API ID: {W}"))
        bot_kernel.config["api_hash"] = input(f"{G}API HASH: {W}")
        bot_kernel.save_config()
    
    client = TelegramClient('forelka', bot_kernel.config["api_id"], bot_kernel.config["api_hash"])
    bot_kernel.client = client
    await client.connect()
    
    await Authenticator(client, banner).start()
    await bot_kernel.init_owner()
    await auto_setup(client)
    
    bot_kernel.aiobot = Bot(
        token=bot_kernel.config["bot_token"], 
        default=DefaultBotProperties(parse_mode="HTML")
    )
    bot_kernel.dp = Dispatcher()

    @bot_kernel.dp.inline_query()
    async def inline_handler(iq: aiotypes.InlineQuery):
        if not bot_kernel.is_owner(iq.from_user.id):
            return await iq.answer([], cache_time=3600)
        q = iq.query or "Forelka"
        text, buttons = q, None
        if "|" in q:
            parts = q.split("|", 1)
            text, buttons = parts[0].strip(), parts[1].strip()
        await bot_kernel.answer_inline(iq, text, buttons)

    @bot_kernel.dp.callback_query()
    async def callback_handler(call: aiotypes.CallbackQuery):
        if not bot_kernel.is_owner(call.from_user.id):
            return await call.answer("Нет доступа", show_alert=True)
        data = call.data
        if data.startswith("cfg_toggle_"):
            _, _, mod, key = data.split("_", 3)
            fk = f"{mod}:{key}"
            bot_kernel.config[fk] = not bot_kernel.config.get(fk, False)
            bot_kernel.save_config()
            await call.answer("OK")
            await bot_kernel.client.send_message("me", ".cfg")
        elif data.startswith("cfg_show_"):
            _, _, mod, key = data.split("_", 3)
            await bot_kernel.client.send_message("me", f".cfg show {mod} {key}")
            await call.answer("Done")
        elif data.startswith("cfg_help_"):
            _, _, mod, key = data.split("_", 3)
            await call.answer(f".f {mod} {key} [value]", show_alert=True)

    for path, pkg in [("forelka/modules", "forelka.modules"), ("modules", "modules")]:
        if not os.path.exists(path):
            os.makedirs(path)
            continue
        for file in os.listdir(path):
            if file.endswith(".py") and not file.startswith("__"):
                try:
                    importlib.import_module(f"{pkg}.{file[:-3]}")
                except Exception as e:
                    print(f"{R}Error loading {file}: {e}{W}")
    
    if "last_reboot" in bot_kernel.config:
        try:
            lr = bot_kernel.config["last_reboot"]
            await client.edit_message(lr["chat"], lr["msg"], bot_kernel.render(
                f"<emoji id=ok,default=✔️> <b>Online</b>\n"
                f"<b>Uptime:</b> <code>{bot_kernel.get_uptime()}</code>"
            ))
        except: pass
        bot_kernel.config.pop("last_reboot", None)
        bot_kernel.save_config()
    
    print(f"{G}Bot is running...{W}")
    await asyncio.gather(
        client.run_until_disconnected(),
        bot_kernel.dp.start_polling(bot_kernel.aiobot)
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()