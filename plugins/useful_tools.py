from telethon import events
import asyncio

# ==========================================
# 1. .button - The Link Button Creator
# ==========================================
@events.register(events.NewMessage(pattern=r"\.button", outgoing=True))
async def link_button(event):
    """Creates a clickable markdown link that looks like a button."""
    # Get the text after the command
    raw_text = event.text.split(" ", 1)
    
    if len(raw_text) < 2:
        await event.edit("❌ **Usage:** `.button Name | Link | Text`")
        return

    # Split by the "|" symbol
    args = raw_text[1].split("|")
    
    if len(args) < 2:
         await event.edit("❌ **Error:** Separator `|` missing.\nUsage: `.button Google | https://google.com | Click Here`")
         return

    # Extract parts
    btn_name = args[0].strip()
    btn_link = args[1].strip()
    # If there is a 3rd part (Text), use it. Otherwise use a default.
    msg_text = args[2].strip() if len(args) > 2 else "Click the link below:"

    # Create the Markdown Link
    markdown_link = f"**{msg_text}**\n\n[ 🔗 {btn_name} ]({btn_link})"
    
    await event.edit(markdown_link, link_preview=False)

# ==========================================
# 2. .google - Let Me Google That For You
# ==========================================
@events.register(events.NewMessage(pattern=r"\.google", outgoing=True))
async def lmgtfy(event):
    """Creates a 'Let Me Google That For You' link."""
    input_str = event.text.split(" ", 1)
    
    if len(input_str) < 2:
        await event.edit("❌ **Usage:** `.google <search query>`")
        return

    query = input_str[1]
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    
    await event.edit(f"Here is what I found for **'{query}'**:\n\n[🔎 Search on Google]({search_url})")

# ==========================================
# 3. .calc - Quick Calculator
# ==========================================
@events.register(events.NewMessage(pattern=r"\.calc", outgoing=True))
async def calculator(event):
    """Basic calculator for math expressions."""
    input_str = event.text.split(" ", 1)
    
    if len(input_str) < 2:
        await event.edit("❌ **Usage:** `.calc <math problem>`")
        return

    expression = input_str[1]
    
    try:
        # 'eval' whitelist to prevent code injection
        allowed_chars = "0123456789+-*/.() "
        if any(char not in allowed_chars for char in expression):
             await event.edit("❌ **Error:** Invalid characters. Only use numbers and + - * /")
             return
             
        # Calculate
        result = eval(expression)
        
        await event.edit(f"🧮 **Calculator**\n\n`{expression}`\n**= {result}**")
        
    except Exception as e:
        await event.edit(f"❌ **Math Error:** {e}")


# ==========================================
# REGISTER FUNCTION (REQUIRED FOR YOUR BOT)
# ==========================================
def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    # Add our event handlers
    client.add_event_handler(link_button)
    client.add_event_handler(lmgtfy)
    client.add_event_handler(calculator)
    
    # Add help info
    help_dict['Useful Tools'] = (
        "**Useful Tools Plugin**\n"
        "`.button Name | Link | Text` - Create a fake button link.\n"
        "`.google <text>` - Send a Google Search link.\n"
        "`.calc <math>` - Simple calculator (e.g., `.calc 5*5`)."
    )
