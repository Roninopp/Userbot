import asyncio
from telethon import events, functions, Button
from telethon import TelegramClient

# ==============================================================================
# ⚠️ CONFIGURATION
# ==============================================================================
# Paste your Bot Token inside the quotes below:
HELPER_BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
# ==============================================================================

# Initialize Helper Bot
try:
    # Changed session name slightly to ensure fresh start
    bot_client = TelegramClient('my_helper_bot_v2', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')
except Exception as e:
    bot_client = None
    print(f"Error init bot: {e}")

# ==========================================
# 1. .realbtn - MULTIPLE BUTTONS SUPPORT
# ==========================================
@events.register(events.NewMessage(pattern=r"\.realbtn", outgoing=True))
async def real_button_command(event):
    """Sends a message with MULTIPLE Inline Keyboard buttons."""
    
    # 1. Check Configuration
    if HELPER_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        return await event.edit("❌ **Error:** Edit `useful_tools.py` and add your `HELPER_BOT_TOKEN`.")

    # 2. Check Connection
    if bot_client is None or not bot_client.is_connected():
        await event.edit("⚠️ Helper Bot is disconnected. Attempting to reconnect...")
        try:
            await bot_client.connect()
        except:
            return await event.edit("❌ **Error:** Helper Bot cannot connect. Check your Token.")

    # 3. Parse Inputs
    # Syntax: .realbtn Message Text | Name:Link | Name:Link
    raw_args = event.text.split(" ", 1)
    if len(raw_args) < 2:
        return await event.edit("❌ **Usage:** `.realbtn Text | Name:Link | Name:Link`")

    # Split by '|'
    parts = raw_args[1].split("|")
    if len(parts) < 2:
        return await event.edit("❌ **Format:** `.realbtn Message | ButtonName:https://link.com`")

    msg_text = parts[0].strip()
    
    # Pack the buttons into the query string
    # We use '||' to separate buttons in the hidden query
    btn_data_list = []
    for btn_part in parts[1:]:
        btn_data_list.append(btn_part.strip())
    
    btn_query_str = "||".join(btn_data_list)

    # Get Bot Username
    try:
        bot_me = await bot_client.get_me()
    except:
        return await event.edit("❌ Error: Helper Bot token is invalid.")

    await event.delete()

    # 4. Send Query
    # Query format: "multi|Message|Btn1:Link||Btn2:Link"
    full_query = f"multi|{msg_text}|{btn_query_str}"
    
    try:
        results = await event.client.inline_query(bot_me.username, full_query)
        await results[0].click(event.chat_id)
    except TimeoutError:
        await event.respond("❌ **Timeout:** Telegram API is slow or Bot is sleeping. Try again.")
    except Exception as e:
        await event.respond(f"❌ **Error:** {e}")


# --- Helper Bot Logic (Handles the Query) ---
@bot_client.on(events.InlineQuery)
async def inline_handler(event):
    query = event.text
    builder = event.builder

    if query.startswith("multi|"):
        try:
            # 1. Split the main parts
            # "multi|Message|Btn1:Link||Btn2:Link"
            main_parts = query.split("|", 2) 
            text_content = main_parts[1]
            buttons_raw = main_parts[2]

            # 2. Process Buttons
            # Split by '||' to get individual buttons
            individual_btns = buttons_raw.split("||")
            
            row = []
            for item in individual_btns:
                # Split by ':' to get Name and Link
                if ":" in item:
                    name, link = item.split(":", 1)
                    row.append(Button.url(name.strip(), link.strip()))
            
            # 3. Create Result
            # We put 'row' inside another list [] to make them side-by-side
            # If you want them stacked (one per line), change [row] to [[b] for b in row]
            result = builder.article(
                title="Send Buttons",
                text=text_content,
                buttons=[row] 
            )
            await event.answer([result])
        except Exception as e:
            print(f"Inline Error: {e}")


# ==========================================
# 2. OLD TOOLS
# ==========================================
@events.register(events.NewMessage(pattern=r"\.button", outgoing=True))
async def link_button(event):
    raw_text = event.text.split(" ", 1)
    if len(raw_text) < 2: return await event.edit("Usage: `.button Name | Link | Text`")
    args = raw_text[1].split("|")
    if len(args) < 2: return await event.edit("Error: Use `|` separator.")
    btn_name = args[0].strip()
    btn_link = args[1].strip()
    msg_text = args[2].strip() if len(args) > 2 else "Click below:"
    await event.edit(f"**{msg_text}**\n\n[ 🔗 {btn_name} ]({btn_link})", link_preview=False)

@events.register(events.NewMessage(pattern=r"\.google", outgoing=True))
async def lmgtfy(event):
    input_str = event.text.split(" ", 1)
    if len(input_str) < 2: return await event.edit("Usage: `.google <query>`")
    query = input_str[1]
    await event.edit(f"Here: [🔎 Search Google](https://www.google.com/search?q={query.replace(' ', '+')})")

@events.register(events.NewMessage(pattern=r"\.calc", outgoing=True))
async def calculator(event):
    input_str = event.text.split(" ", 1)
    if len(input_str) < 2: return await event.edit("Usage: `.calc 5+5`")
    try:
        await event.edit(f"🧮 `{input_str[1]}` = **{eval(input_str[1])}**")
    except: await event.edit("Error: Invalid Math")

# ==========================================
# REGISTRATION
# ==========================================
async def start_helper_bot():
    if not bot_client: return
    try:
        await bot_client.start(bot_token=HELPER_BOT_TOKEN)
        await bot_client.run_until_disconnected()
    except Exception as e:
        print(f"Helper Bot Crash: {e}")

def register(client, help_dict):
    client.add_event_handler(real_button_command)
    client.add_event_handler(link_button)
    client.add_event_handler(lmgtfy)
    client.add_event_handler(calculator)
    
    if HELPER_BOT_TOKEN != "PASTE_YOUR_BOT_TOKEN_HERE":
        client.loop.create_task(start_helper_bot())

    help_dict['Useful Tools'] = (
        "**Multi-Button Update**\n"
        "Usage: `.realbtn Text | Name:Link | Name2:Link2`\n"
        "Example: `.realbtn Hello | Google:google.com | Bing:bing.com`"
    )
