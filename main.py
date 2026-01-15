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

# --- CONFIGURATION ---
# PASTE YOUR DATA HERE DIRECTLY
# Replace 123456 with your integer App ID
# Replace "YOUR_HASH" and "YOUR_SESSION" with your actual strings (keep the quotes!)

API_ID = 123456  
API_HASH = "YOUR_API_HASH_HERE"
STRING_SESSION = "YOUR_LONG_STRING_SESSION_HERE"

# --- SAFETY CHECK ---
# This ensures you actually replaced the values above.
# We check against the placeholders to see if you edited them.
if API_ID == 123456 or API_HASH == "YOUR_API_HASH_HERE" or STRING_SESSION == "YOUR_LONG_STRING_SESSION_HERE":
    # If using Environment Variables (Heroku Config Vars) instead, we try to load them here:
    API_ID = os.environ.get("TELEGRAM_API_ID") or API_ID
    API_HASH = os.environ.get("TELEGRAM_API_HASH") or API_HASH
    STRING_SESSION = os.environ.get("STRING_SESSION") or STRING_SESSION

    # If STILL generic, we stop safely.
    if str(API_ID) == "123456" or API_HASH == "YOUR_API_HASH_HERE":
        logger.critical("STOPPING: Please paste your API_ID, API_HASH, and STRING_SESSION in main.py!")
        sys.exit(1)

# This dictionary will hold help messages for loaded plugins
PLUGINS = {}
PLUGIN_PATH = "plugins"

# --- PLUGIN LOADER ---
sys.path.append(os.path.abspath(PLUGIN_PATH))

def load_plugins():
    """Finds, imports, and registers all plugins in the 'plugins' directory."""
    logger.info(f"Loading plugins from '{PLUGIN_PATH}'...")
    
    if not os.path.isdir(PLUGIN_PATH):
        logger.warning(f"Plugin directory '{PLUGIN_PATH}' not found. Creating it.")
        os.makedirs(PLUGIN_PATH)
        return

    for f in os.listdir(PLUGIN_PATH):
        if f.endswith(".py") and f != "__init__.py":
            plugin_name = f[:-3]  # Remove '.py'
            try:
                module = importlib.import_module(plugin_name)
                
                # Check for the 'register' function and call it
                if hasattr(module, 'register'):
                    module.register(client, PLUGINS)
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} has no 'register' function.")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}:", exc_info=True)

# --- INITIALIZE CLIENT ---
try:
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
except Exception as e:
    logger.critical(f"Failed to initialize client. Check your String Session! Error: {e}")
    sys.exit(1)

@client.on(events.NewMessage(pattern=r'\.help', outgoing=True))
async def help_handler(event):
    """Handler for the .help command."""
    if not PLUGINS:
        await event.edit("No plugins loaded.")
        return

    help_text = "**Available Plugins:**\n\n"
    for plugin_name, help_msg in PLUGINS.items():
        help_text += f"**Module: `{plugin_name}`**\n{help_msg}\n\n"
    
    await event.edit(help_text)

async def main():
    """Main function to start the bot."""
    logger.info("Starting userbot...")
    await client.start()
    
    load_plugins() 
    
    me = await client.get_me()
    logger.info(f"Userbot started successfully as {me.first_name} (@{me.username})!")
    logger.info("Send .help in any chat (that you can type in) to see available commands.")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    # FIX FOR HEROKU/PYTHON 3.10+
    # Explicitly create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
