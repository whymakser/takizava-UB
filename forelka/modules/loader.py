import os
import aiohttp
import importlib
from telethon import events
from __main__ import bot_kernel as bot

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.lm"))
async def load_module_reply(event):
    if not bot.is_targeted(event): return
    reply = await event.get_reply_message()
    
    if not reply or not reply.file or not reply.file.name.endswith(".py"):
        return await bot.edit(event, "<emoji id=ok,default=⚠️> <b>Reply to a .py file!</b>")
    
    module_name = reply.file.name
    path = f"modules/{module_name}"
    
    if not os.path.exists("modules"): os.makedirs("modules")
    
    await bot.edit(event, f"<emoji id=reload,default=⏳> <b>Loading</b> <code>{module_name}</code><b>...</b>")
    await bot.client.download_media(reply, path)
    
    try:
        importlib.import_module(f"modules.{module_name[:-3]}")
        await bot.edit(event, f"<emoji id=ok,default=✔️> <b>Module</b> <code>{module_name}</code> <b>loaded into /modules/!</b>")
    except Exception as e:
        if os.path.exists(path): os.remove(path)
        await bot.edit(event, f"<emoji id=ok,default=❌> <b>Error:</b>\n<code>{e}</code>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.dlm (?P<url>.+)"))
async def download_load_module(event):
    if not bot.is_targeted(event): return
    url = event.pattern_match.group("url").strip()
    module_name = url.split("/")[-1]
    
    if not module_name.endswith(".py"):
        module_name += ".py"
        
    path = f"modules/{module_name}"
    if not os.path.exists("modules"): os.makedirs("modules")
    
    await bot.edit(event, f"<emoji id=reload,default=⏳> <b>Downloading</b> <code>{module_name}</code><b>...</b>")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200: raise Exception(f"Status {resp.status}")
                content = await resp.read()
                with open(path, "wb") as f: f.write(content)
        
        importlib.import_module(f"modules.{module_name[:-3]}")
        await bot.edit(event, f"<emoji id=ok,default=✔️> <b>Module</b> <code>{module_name}</code> <b>downloaded to /modules/!</b>")
    except Exception as e:
        if os.path.exists(path): os.remove(path)
        await bot.edit(event, f"<emoji id=ok,default=❌> <b>Error:</b>\n<code>{e}</code>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.ulm (?P<name>.+)"))
async def unload_module(event):
    if not bot.is_targeted(event): return
    module_name = event.pattern_match.group("name").strip()
    if not module_name.endswith(".py"): module_name += ".py"
    
    path = f"modules/{module_name}"
    
    if os.path.exists(path):
        os.remove(path)
        await bot.edit(event, f"<emoji id=ok,default=✔️> <b>Module</b> <code>{module_name}</code> <b>removed from /modules/.</b>\n<b>Restart required.</b>")
    else:
        await bot.edit(event, "<emoji id=ok,default=⚠️> <b>Module not found in /modules/.</b>")

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.ml (?P<name>.+)"))
async def send_module(event):
    if not bot.is_targeted(event): return
    module_name = event.pattern_match.group("name").strip()
    if not module_name.endswith(".py"): module_name += ".py"
    
    paths = [f"modules/{module_name}", f"forelka/modules/{module_name}"]
    
    for path in paths:
        if os.path.exists(path):
            await bot.client.send_file(event.chat_id, path, caption=f"<emoji id=ok,default=📦> <b>Module:</b> <code>{module_name}</code>\n<b>Path:</b> <code>{path}</code>")
            return await event.delete()
            
    await bot.edit(event, "<emoji id=ok,default=⚠️> <b>Module not found in any directory.</b>")