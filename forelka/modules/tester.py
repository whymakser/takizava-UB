import time
import sys
import os
import io
from telethon import events
from __main__ import bot_kernel as bot

@bot.client.on(events.NewMessage(pattern=r"(?s)^\.ping$"))
async def ping_handler(event):
    if not bot.is_targeted(event):
        return
    
    start = time.perf_counter()
    message = await bot.edit(event, "<b>Pinging...</b>")
    end = time.perf_counter()
    
    latency = (end - start) * 1000
    await bot.edit(message, f"<b>Pong!</b>\n<code>{latency:.2f}ms</code>")

@bot.client.on(events.NewMessage(pattern=r"(?s)^\.restart$"))
async def restart_handler(event):
    if not bot.is_targeted(event):
        return
    
    await bot.edit(event, "<b>Restarting...</b>")
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.client.on(events.NewMessage(pattern=r"(?s)^\.exec (?P<args>.*)"))
async def exec_handler(event):
    if not bot.is_targeted(event):
        return
    
    code = event.pattern_match.group("args")
    await bot.edit(event, "<b>Executing...</b>")
    
    try:
        output = io.StringIO()
        exec(f"async def __ex(event, bot): " + "".join(f"\n {l}" for l in code.split("\n")), globals())
        await locals()["__ex"](event, bot)
        result = "<b>Success</b>"
    except Exception as e:
        result = f"<b>Error:</b>\n<code>{str(e)}</code>"
    
    if len(result) > 4096:
        file = io.BytesIO(result.encode())
        file.name = "output.txt"
        await bot.client.send_file(event.chat_id, file, caption="<b>Output too long</b>")
    else:
        await bot.edit(event, result)