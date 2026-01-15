import os
import importlib
import logging
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION (HARDCODED) ---

# 1. PASTE YOUR API_ID HERE (It must be an Integer, no quotes usually)
API_ID = 21502134  

# 2. PASTE YOUR API_HASH HERE (Keep the quotes)
API_HASH = "e09a3f453b841ca4d1823d3b4004672d"

# 3. PASTE YOUR STRING_SESSION HERE (Keep the quotes)
STRING_SESSION = "1BVtsOIUBu1hzkoj6vU8vylkocPQvllfTwSy6davvVEL-BdRoEF856DoCawWgF-drPu-v4PI_lVxB_v4BaCB5-Xo5-cu5BEGlRuBpM4D6gmKpgqsVuw7kOS2UP9wqJEtZzCdaT0Sa5ITHPe6xzhK1UoYy7zCNnaZVuYu1BgMfaMxHzwP6M0CeC_xkcwpW8Cgm0OTpXNoZaNNeD_EnRr6dMxMiPTb36_80iwza7bhNrzdKciVR14ameJiybHMdbCWZ5AiKBBGKlEQHEAIe_qx-qiJAwPJjzwsrThkrOsUV0DlFTymAJpcR5X9Os0t1L7IOzRyohVnsv-7FVkR5sVqDjhZggnGrWjY="

# --- SAFETY CHECK ---
# We check if you actually filled them in. If not, we log an error and stop safely instead of crashing.
if API_ID == 1234567 or API_HASH == "paste_your_api_hash_here_inside_quotes":
    logger.critical("STOPPING: You did not replace the placeholder API_ID or API_HASH in main.py!")
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
    client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)
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
    await client.start()
    
    load_plugins()
    
    me = await client.get_me()
    logger.info(f"Userbot started successfully as {me.first_name} (@{me.username})!")
    logger.info("Send .help in any chat to see available commands.")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
