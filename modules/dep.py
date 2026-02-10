import random
import aiohttp
from telethon import events
from __main__ import bot_kernel as bot

__config__ = {
    "cpay_token": {
        "type": "string",
        "title": "CryptoPay Token",
        "desc": "Токен от @CryptoTestnetBot",
        "spoiler": True
    },
    "chance": {
        "type": "string", 
        "title": "Chance %",
        "desc": "Шанс успеха (0.1 = 10%)",
        "default": "0.1"
    }
}

async def request_crypto_pay(method, params=None):
    token = bot.config.get("gambler:cpay_token")
    if not token: return {"ok": False, "description": "Token not set in .cfg"}
    
    headers = {"Crypto-Pay-API-Token": token}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://testnet-pay.cryptobot.pay/api/{method}", params=params, headers=headers) as resp:
            return await resp.json()

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.dep"))
async def deposit_gamble(event):
    if not bot.is_targeted(event): return
    
    # Берем шанс из конфига
    chance = float(bot.config.get("gambler:chance", 0.1))
    
    if random.random() > chance:
        return await bot.edit(event, "<emoji id=ok,default=⚠️> <b>Luck is not on your side.</b>")
    
    await bot.edit(event, "<emoji id=reload,default=⏳> <b>Generating 10 USDT invoice...</b>")
    
    res = await request_crypto_pay("createInvoice", {
        "asset": "USDT",
        "amount": "10",
        "description": "Deposit Gamble"
    })
    
    if res.get("ok"):
        pay_url = res["result"]["pay_url"]
        await bot.edit(
            event, 
            f"<emoji id=ok,default=🪙> <b>Lucky! Deposit required:</b> 10 USDT",
            buttons=f"<Pay Now>[{pay_url}]"
        )
    else:
        await bot.edit(event, f"<emoji id=error,default=❌> <b>Error:</b> <code>{res.get('description')}</code>")