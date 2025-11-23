import asyncio
import random
import string
from telethon import events, functions, Button
from telethon import TelegramClient

# ==============================================================================
# ⚠️ CONFIGURATION
# ==============================================================================
HELPER_BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
# ==============================================================================

# Initialize Helper Bot
try:
    bot_client = TelegramClient('helper_bot_v3', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')
except Exception as e:
    bot_client = None
    print(f"Error init bot: {e}")

# Global Memory Storage (The Trick)
# We store the long text here and just pass a small key to the bot
MESSAGE_STORE = {}

def generate_key():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# ==========================================
# 1. .realbtn - HEAVY DUTY VERSION
# ==========================================
@events.register(events.NewMessage(pattern=r"\.realbtn", outgoing=True))
async def real_button_command(event):
    """Sends a message with MULTIPLE Inline Keyboard buttons (Unlimited Text Size)."""
    
    # 1. Config Check
    if HELPER_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        return await event.edit("❌ **Error:** Add your `HELPER_BOT_TOKEN` in the plugin file.")

    # 2. Connection Check
    if bot_client is None or not bot_client.is_connected():
        await event.edit("⚠️ Helper Bot connecting...")
        try:
            await bot_client.connect()
        except:
            return await event.edit("❌ **Error:** Helper Bot cannot connect. Check Token.")

    # 3. Parse Inputs
    # Syntax: .realbtn Message | Name:Link | Name:Link
    raw_args = event.text.split(" ", 1)
    if len(raw_args) < 2:
        return await event.edit("❌ **Usage:** `.realbtn Text | Name:Link | Name:Link`")

    # Split by '|'
    parts = raw_args[1].split("|")
    if len(parts) < 2:
        return await event.edit("❌ **Format:** `.realbtn Message | ButtonName:https://link.com`")

    msg_text = parts[0].strip()
    
    # 4. Process Buttons
    buttons_list = []
    for btn_part in parts[1:]:
        if ":" in btn_part:
            name, link = btn_part.split(":", 1)
            # Create a Button Object here to store in memory
            buttons_list.append(Button.url(name.strip(), link.strip()))
    
    if not buttons_list:
        return await event.edit("❌ **Error:** No valid buttons found. Use `Name:Link` format.")

    # 5. THE MEMORY TRICK
    # Instead of sending text, we generate a key
    unique_key = generate_key()
    
    # Save the huge text and buttons in our global dictionary
    MESSAGE_STORE[unique_key] = {
        'text': msg_text,
        'buttons': [buttons_list] # Double list for rows
    }

    # Get Bot Username
    try:
        bot_me = await bot_client.get_me()
    except:
        return await event.edit("❌ Error: Helper Bot token is invalid.")

    await event.delete()

    # 6. Send Tiny Query
    # We only send "fetch|key", which is super short!
    query_text = f"fetch|{unique_key}"
    
    try:
        # Ask helper bot to fetch the message by key
        results = await event.client.inline_query(bot_me.username, query_text)
        await results[0].click(event.chat_id)
    except TimeoutError:
        await event.respond("❌ **Timeout:** Telegram API slow. Try again.")
    except IndexError:
        await event.respond("❌ **Error:** Bot didn't return a result. Is Inline Mode on?")
    except Exception as e:
        await event.respond(f"❌ **Error:** {e}")


# --- Helper Bot Logic (Fetches from Memory) ---
@bot_client.on(events.InlineQuery)
async def inline_handler(event):
    query = event.text
    builder = event.builder

    if query.startswith("fetch|"):
        try:
            # 1. Get the key
            _, key = query.split("|")
            
            # 2. Retrieve data from Global Memory
            if key in MESSAGE_STORE:
                data = MESSAGE_STORE[key]
                
                result = builder.article(
                    title="Send Big Message",
                    text=data['text'],
                    buttons=data['buttons'],
                    link_preview=True 
                )
                await event.answer([result])
            else:
                # Key not found (expired or restart)
                pass
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
