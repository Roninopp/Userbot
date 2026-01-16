import os
import importlib
import logging
import sys
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- FIX FOR PYTHON 3.10+ & HEROKU ---
# We must create the loop BEFORE creating the client
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
# -------------------------------------

# --- CONFIGURATION (YOUR CREDENTIALS) ---
API_ID = 21502134
API_HASH = "e09a3f453b841ca4d1823d3b4004672d"

# I added .strip() to ensure no invisible spaces cause errors
STRING_SESSION = "1BVtsOIABu3-55YOPSHgbu7n9askvcjCgjO5rno8yAtFI4cNcR_RgZ8MS3Da4ZfwUatjPnFK6Q4OMk2a9gNfc-Dt0KpU5lWNcOBBGkVyP0HP0imtNgo7MjduDJiXl7mQ6ABKsS2CWURw7ik--F8hkARobM6NQfcnRHuF4eeeSNlJF2Vtvow2_5zszvpKnv_zscYUJOcFKfy8ppL4FN9Teo5qA6x0ixAcc7tvamv46AEw6dGVIzz7re_Eptl7o8pHgpWKBh-T5jPebdpLZI3ivS2BSeV_faT8xHAe-OjZcib5oqYWs3HJMkdSKxxSlpJH7Lf4kPbqGqdoXhaxMZ4eWHPX5k3SJVdg=".strip()

# This dictionary will hold help messages for loaded plugins
PLUGINS = {}
PLUGIN_PATH = "plugins"

# --- PLUGIN LOADER ---
sys.path.append(os.path.abspath(PLUGIN_PATH))

def load_plugins():
    logger.info(f"Loading plugins from '{PLUGIN_PATH}'...")
    if not os.path.isdir(PLUGIN_PATH):
        logger.warning(f"Plugin directory '{PLUGIN_PATH}' not found. Creating it.")
        os.makedirs(PLUGIN_PATH)
        return

    for f in os.listdir(PLUGIN_PATH):
        if f.endswith(".py") and f != "__init__.py":
            plugin_name = f[:-3]
            try:
                module = importlib.import_module(plugin_name)
                if hasattr(module, 'register'):
                    module.register(client, PLUGINS)
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} has no 'register' function.")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}:", exc_info=True)

# --- INITIALIZE CLIENT ---
try:
    # We pass 'loop=loop' to fix the Runtime error
    client = TelegramClient(
        StringSession(STRING_SESSION), 
        API_ID, 
        API_HASH,
        loop=loop
    )
except Exception as e:
    logger.critical(f"Failed to initialize client. Check your String Session! Error: {e}")
    sys.exit(1)

@client.on(events.NewMessage(pattern=r'\.help', outgoing=True))
async def help_handler(event):
    if not PLUGINS:
        await event.edit("No plugins loaded.")
        return

    help_text = "**Available Plugins:**\n\n"
    for plugin_name, help_msg in PLUGINS.items():
        help_text += f"**Module: `{plugin_name}`**\n{help_msg}\n\n"
    
    await event.edit(help_text)

async def main():
    logger.info("Starting userbot...")
    
    # We use await client.connect() instead of start() to avoid the interactive prompt
    await client.connect()
    
    if not await client.is_user_authorized():
        logger.critical("CRITICAL ERROR: String Session is invalid or expired. Please generate a new one.")
        return

    load_plugins() 
    
    me = await client.get_me()
    logger.info(f"Userbot started successfully as {me.first_name} (@{me.username})!")
    logger.info("Send .help in any chat to see available commands.")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Run the loop we created at the top
    loop.run_until_complete(main())
