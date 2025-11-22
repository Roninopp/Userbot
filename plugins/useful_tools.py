from telethon import events, Button, functions
from telethon.tl.custom import Button as CustomButton
import asyncio

# ==============================================================================
# ⚠️ CONFIGURATION - YOU MUST FILL THIS FOR BUTTONS TO WORK
# ==============================================================================
# 1. Go to @BotFather, create a bot, and get the token.
# 2. Paste the token inside the quotes below.
BOT_TOKEN = "8405972806:AAHx_Wlpf3SKt6mIypp_1pU7uG8lS_2M4nk" 
# ==============================================================================

# We need a separate client for the bot to handle the buttons
try:
    from telethon import TelegramClient
    # We use a unique session name for the helper bot
    bot_client = TelegramClient('helper_bot_session', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e')
    bot_client.start(bot_token=BOT_TOKEN)
except Exception as e:
    print(f"❌ HELPER BOT ERROR: Could not start. Did you put the token? {e}")
    bot_client = None

# 1. The Command to Trigger the Button
# Usage: .realbtn Text | Link | Button Name
@events.register(events.NewMessage(pattern=r"\.realbtn", outgoing=True))
async def real_button_command(event):
    if bot_client is None:
        await event.edit("❌ **Error:** You didn't add the `BOT_TOKEN` in the plugin file!")
        return

    # Parse inputs
    args = event.text.split(" ", 1)
    if len(args) < 2:
        await event.edit("❌ Usage: `.realbtn Text | Link | Button Name`")
        return

    parts = args[1].split("|")
    if len(parts) != 3:
        await event.edit("❌ Format: `.realbtn Message Text | https://link.com | Button Label`")
        return

    msg_text = parts[0].strip()
    link_url = parts[1].strip()
    btn_label = parts[2].strip()

    # Get the bot's username
    bot_me = await bot_client.get_me()
    bot_username = bot_me.username

    # Delete the user's command
    await event.delete()

    # Use Inline Query to ask the Helper Bot to send the button
    # We construct a query: "button|Text|Link|Label"
    query_text = f"button|{msg_text}|{link_url}|{btn_label}"
    
    try:
        results = await event.client.inline_query(bot_username, query_text)
        await results[0].click(event.chat_id)
    except Exception as e:
        await event.respond(f"❌ Failed to send button. Make sure @{bot_username} is started and has Inline Mode enabled in BotFather.\nError: {e}")


# 2. The Bot Logic (Handles the Inline Query)
@bot_client.on(events.InlineQuery)
async def inline_handler(event):
    builder = event.builder
    query = event.text
    
    # Check if the query is for our button command
    if query.startswith("button|"):
        try:
            _, text, url, label = query.split("|")
            
            # Create the result with the button
            result = builder.article(
                title="Send Button",
                text=text,
                buttons=[[Button.url(label, url)]]
            )
            await event.answer([result])
        except Exception:
            pass # Ignore malformed queries

# Registration (Standard for your bot)
def register(client, help_dict):
    client.add_event_handler(real_button_command)
    
    # We also need to run the bot client in the background
    if bot_client:
        client.loop.create_task(bot_client.run_until_disconnected())

    help_dict['Real Button'] = (
        "**.realbtn <text> | <link> | <label>**\n"
        "Sends a message with a REAL Inline Keyboard button.\n"
        "⚠️ Requires `BOT_TOKEN` to be set in the plugin file."
    )
