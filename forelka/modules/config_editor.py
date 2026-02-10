import sys
from telethon import events
from __main__ import bot_kernel as bot

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.cfg"))
async def universal_config(event):
    if not bot.is_targeted(event): return
    
    all_configs = {}
    for mod_name, module in sys.modules.items():
        if (mod_name.startswith("modules.") or mod_name.startswith("forelka.modules.")) and hasattr(module, "__config__"):
            all_configs[mod_name.split(".")[-1]] = module.__config__

    if not all_configs: return await bot.edit(event, "❌ <b>Модули не найдены.</b>")

    args = event.text.split()
    show_mod = args[2] if len(args) > 3 and args[1] == "show" else None
    show_key = args[3] if len(args) > 3 and args[1] == "show" else None

    text = "⚙️ <b>Конфигурация:</b>\n"
    buttons = ""

    for mod, params in all_configs.items():
        text += f"\n📦 <b>Модуль:</b> <code>{mod}</code>\n"
        for key, info in params.items():
            current = bot.config.get(f"{mod}:{key}", "<i>Not set</i>")
            is_spoiler = info.get("spoiler", False)
            
            if is_spoiler and current != "<i>Not set</i>":
                if show_mod == mod and show_key == key:
                    display_val = f"<tg-spoiler>{current}</tg-spoiler>"
                else:
                    display_val = "<code>**********</code>"
            else:
                display_val = f"<code>{current}</code>"

            text += f"  • <b>{info['title']}</b>: {display_val}\n"
            
            if info['type'] == 'string':
                if is_spoiler and not (show_mod == mod and show_key == key):
                    buttons += f"<{info['title']}: Show>[cfg_show_{mod}_{key}]"
                buttons += f"<{info['title']}: Edit>[cfg_help_{mod}_{key}]"
            elif info['type'] == 'bool':
                label = "✅ ON" if current is True else "❌ OFF"
                buttons += f"<{info['title']}: {label}>[cfg_toggle_{mod}_{key}]"
    
    await bot.query.send(event.chat_id, text, buttons=buttons)
    await event.delete()

@bot.client.on(events.NewMessage(outgoing=True, pattern=r"(?s)^\.f\s+(?P<mod>\w+)\s+(?P<key>\w+)\s+(?P<val>.*)"))
async def fill_config(event):
    if not bot.is_targeted(event): return
    m, k, v = event.pattern_match.group("mod"), event.pattern_match.group("key"), event.pattern_match.group("val")
    bot.config[f"{m}:{k}"] = v.strip()
    bot.save_config()
    await bot.edit(event, f"✔️ <b>Saved:</b> <code>{m}:{k}</code>")