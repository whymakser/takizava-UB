from __main__ import bot_kernel as bot
import asyncio
from telethon import events
client = bot.client
dp = bot.dp


@client.on(events.NewMessage(outgoing=True, pattern=r"^\.tunnel"))
async def tn(event):
    await bot.edit(event, "<emoji id=globe,default=🌐> <b>Starting...</b>")
    p = await asyncio.create_subprocess_shell("ssh -R 80:localhost:8080 nokey@localhost.run", stdout=-1)
    l = await p.stdout.readline()
    await bot.edit(event, f"<emoji id=ok,default=✔️> <code>{l.decode().strip()}</code>")