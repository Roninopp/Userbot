import asyncio
from telethon import events, functions, Button
from telethon import TelegramClient

# ==============================================================================
# ⚠️ CONFIGURATION - REQUIRED FOR REAL BUTTONS
# ==============================================================================
# 1. Get a token from @BotFather
# 2. Enable Inline Mode in BotFather (/setinline)
# 3. Paste the token below inside the quotes:
HELPER_BOT_TOKEN = "8405972806:AAHx_Wlpf3SKt6mIypp_1pU7uG8lS_2M4nk"
# ==============================================================================

# Initialize the Helper Bot Client (but don't start it yet)
try:
    # We use a unique session name so it doesn't conflict
    bot_client = TelegramClient('helper_bot_session', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')
except Exception as e:
    bot_client = None
    print(f"Error initializing helper bot: {e}")


# ==========================================
# 1. .realbtn - THE REAL TELEGRAM BUTTONS
# ==========================================
@events.register(events.NewMessage(pattern=r"\.realbtn", outgoing=True))
async def real_button_command(event):
    """Sends a message with a REAL Inline Keyboard button using the helper bot."""
    
    # Check if the bot token was added
    if HELPER_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        await event.edit("❌ **Error:** You need to edit the plugin file and add your `HELPER_BOT_TOKEN`.")
        return

    if bot_client is None or not await bot_client.is_user_authorized():
        await event.edit("❌ **Error:** Helper Bot is not running. Check your logs.")
        return

    # Parse inputs: .realbtn Text | Link | Label
    args = event.text.split(" ", 1)
    if len(args) < 2:
        await event.edit("❌ Usage: `.realbtn Text | Link | Button Label`")
        return

    parts = args[1].split("|")
    if len(parts) != 3:
        await event.edit("❌ Format: `.realbtn Message Text | https://link.com | Button Label`")
        return

    msg_text = parts[0].strip()
    link_url = parts[1].strip()
    btn_label = parts[2].strip()

    # Get bot username
    bot_me = await bot_client.get_me()
    if not bot_me:
         await event.edit("❌ Error: Could not get Helper Bot info.")
         return

    await event.delete()

    # Trigger the Inline Query
    query_text = f"btn|{msg_text}|{link_url}|{btn_label}"
    try:
        # Ask the helper bot to generate the button
        results = await event.client.inline_query(bot_me.username, query_text)
        # Click the result to send it
        await results[0].click(event.chat_id)
    except Exception as e:
        await event.respond(f"❌ Failed. Ensure @{bot_me.username} has **Inline Mode** enabled in BotFather.\nError: {e}")

# --- Helper Bot Logic (This runs on the second client) ---
@bot_client.on(events.InlineQuery)
async def inline_handler(event):
    query = event.text
    # We use a prefix 'btn|' to know it's our command
    if query.startswith("btn|"):
        try:
            _, text, url, label = query.split("|")
            
            result = event.builder.article(
                title="Send Button",
                text=text,
                buttons=[[Button.url(label, url)]]
            )
            await event.answer([result])
        except Exception:
            pass

# ==========================================
# 2. OLD TOOLS (.button, .google, .calc)
# ==========================================

@events.register(events.NewMessage(pattern=r"\.button", outgoing=True))
async def link_button(event):
    """Fake link button (Blue text)."""
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
    """Google Search Link."""
    input_str = event.text.split(" ", 1)
    if len(input_str) < 2: return await event.edit("Usage: `.google <query>`")
    query = input_str[1]
    await event.edit(f"Here: [🔎 Search Google](https://www.google.com/search?q={query.replace(' ', '+')})")

@events.register(events.NewMessage(pattern=r"\.calc", outgoing=True))
async def calculator(event):
    """Simple Calculator."""
    input_str = event.text.split(" ", 1)
    if len(input_str) < 2: return await event.edit("Usage: `.calc 5+5`")
    try:
        allowed = "0123456789+-*/.() "
        if any(c not in allowed for c in input_str[1]): return await event.edit("Error: Invalid math.")
        await event.edit(f"🧮 `{input_str[1]}` = **{eval(input_str[1])}**")
    except Exception as e: await event.edit(f"Error: {e}")

# ==========================================
# REGISTRATION & STARTUP
# ==========================================
async def start_helper_bot():
    """Starts the helper bot in the background safely."""
    if not bot_client: return
    try:
        # Start the bot with the token
        await bot_client.start(bot_token=HELPER_BOT_TOKEN)
        # Keep it running
        await bot_client.run_until_disconnected()
    except Exception as e:
        print(f"⚠️ Helper Bot Warning: {e}")

def register(client, help_dict):
    # Register commands for the Userbot
    client.add_event_handler(real_button_command)
    client.add_event_handler(link_button)
    client.add_event_handler(lmgtfy)
    client.add_event_handler(calculator)
    
    # Start the Helper Bot in the background using the existing loop
    # This fixes the "coroutine never awaited" error!
    if HELPER_BOT_TOKEN != "PASTE_YOUR_BOT_TOKEN_HERE":
        client.loop.create_task(start_helper_bot())
    else:
        print("⚠️ Plugin Loaded, but Real Buttons disabled (No Token set in useful_tools.py)")

    help_dict['Useful Tools'] = (
        "**Tools & Buttons**\n"
        "`.realbtn Text | Link | Label` - Real Buttons (Requires Helper Bot).\n"
        "`.button Name | Link | Text` - Fake Link Button.\n"
        "`.google <query>` - Search link.\n"
        "`.calc <math>` - Calculator."
    )
