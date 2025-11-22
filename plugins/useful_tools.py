import asyncio
from telethon import events

# --- IMPORT HANDLING ---
# We try to match your bot's variable name (borg, bot, or client)
try:
    from userbot import bot as client
except ImportError:
    try:
        from userbot import borg as client
    except ImportError:
        from userbot import client

# ==========================================
# 1. .button - The Link Button Creator
# ==========================================
# USAGE: .button ButtonName | https://link.com | Your Message Text
# The '|' symbol is used to separate the parts so you can use spaces in the name!
@client.on(events.NewMessage(pattern=r"\.button", outgoing=True))
async def link_button(event):
    # Get the text after the command
    raw_text = event.text.split(" ", 1)
    
    if len(raw_text) < 2:
        await event.edit("❌ **Usage:** `.button Name | Link | Text`")
        return

    # Split by the "|" symbol
    args = raw_text[1].split("|")
    
    if len(args) < 2:
         await event.edit("❌ **Error:** You need to separate Name and Link with a `|` symbol.\nExample: `.button Google | https://google.com | Search here!`")
         return

    # Extract parts
    btn_name = args[0].strip()
    btn_link = args[1].strip()
    # If there is a 3rd part (Text), use it. Otherwise use a default.
    msg_text = args[2].strip() if len(args) > 2 else "Click the link below:"

    # Create the Markdown Link
    # Format: [ Button Name ](Link)
    markdown_link = f"**{msg_text}**\n\n[ 🔗 {btn_name} ]({btn_link})"
    
    await event.edit(markdown_link, link_preview=False)

# ==========================================
# 2. .google - Let Me Google That For You
# ==========================================
# USAGE: .google best pizza recipe
@client.on(events.NewMessage(pattern=r"\.google", outgoing=True))
async def lmgtfy(event):
    input_str = event.text.split(" ", 1)
    
    if len(input_str) < 2:
        await event.edit("❌ **Usage:** `.google <search query>`")
        return

    query = input_str[1]
    # Replace spaces with + for the URL
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    await event.edit(f"Here is what I found for **'{query}'**:\n\n[🔎 Search on Google]({search_url})")

# ==========================================
# 3. .calc - Quick Calculator
# ==========================================
# USAGE: .calc 50 * 12
@client.on(events.NewMessage(pattern=r"\.calc", outgoing=True))
async def calculator(event):
    input_str = event.text.split(" ", 1)
    
    if len(input_str) < 2:
        await event.edit("❌ **Usage:** `.calc <math problem>`")
        return

    expression = input_str[1]
    
    try:
        # 'eval' can be dangerous, so we whitelist only math characters
        allowed_chars = "0123456789+-*/.() "
        if any(char not in allowed_chars for char in expression):
             await event.edit("❌ **Error:** Invalid characters. Only use numbers and + - * /")
             return
             
        # Calculate
        result = eval(expression)
        
        await event.edit(f"🧮 **Calculator**\n\n`{expression}`\n**= {result}**")
        
    except Exception as e:
        await event.edit(f"❌ **Math Error:** {e}")
