import os
import importlib
import logging
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession  # <-- IMPORTED STRING SESSION

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
API_ID = os.environ.get('21502134')
API_HASH = os.environ.get('e09a3f453b841ca4d1823d3b4004672d')

# Paste your string session here between the quotes if you want it direct in the file
# Or leave it as os.environ.get to load it from VPS settings
STRING_SESSION = os.environ.get('1BVtsOIUBu1hzkoj6vU8vylkocPQvllfTwSy6davvVEL-BdRoEF856DoCawWgF-drPu-v4PI_lVxB_v4BaCB5-Xo5-cu5BEGlRuBpM4D6gmKpgqsVuw7kOS2UP9wqJEtZzCdaT0Sa5ITHPe6xzhK1UoYy7zCNnaZVuYu1BgMfaMxHzwP6M0CeC_xkcwpW8Cgm0OTpXNoZaNNeD_EnRr6dMxMiPTb36_80iwza7bhNrzdKciVR14ameJiybHMdbCWZ5AiKBBGKlEQHEAIe_qx-qiJAwPJjzwsrThkrOsUV0DlFTymAJpcR5X9Os0t1L7IOzRyohVnsv-7FVkR5sVqDjhZggnGrWjY=') 

# Fallbacks if env vars are missing
if not API_ID:
    API_ID = input("Please enter your API ID: ")
if not API_HASH:
    API_HASH = input("Please enter your API HASH: ")
if not STRING_SESSION:
    # If you didn't put it in the code or ENV, we ask for it
    STRING_SESSION = input("Please enter your STRING_SESSION: ")

# This dictionary will hold help messages for loaded plugins
PLUGINS = {}
PLUGIN_PATH = "plugins"

# --- NEW PLUGIN LOADER ---
sys.path.append(os.path.abspath(PLUGIN_PATH))

def load_plugins():
    """Finds, imports, and registers all plugins in the 'plugins' directory."""
    logger.info(f"Loading plugins from '{PLUGIN_PATH}'...")
    
    if not os.path.isdir(PLUGIN_PATH):
        logger.warning(f"Plugin directory '{PLUGIN_PATH}' not found. Creating it.")
        os.makedirs(PLUGIN_PATH)
        return

    # Iterate through all files in the plugin directory
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
# --- END OF NEW LOADER ---

# --- INITIALIZE CLIENT WITH STRING SESSION ---
# This tells Telethon to use the string instead of creating a .session file
client = TelegramClient(StringSession(STRING_SESSION), int(API_ID), API_HASH)

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
    
    # We no longer need to check for phone number login here 
    # because StringSession handles authentication immediately.
    await client.start()
    
    load_plugins() 
    
    me = await client.get_me()
    logger.info(f"Userbot started successfully as {me.first_name} (@{me.username})!")
    logger.info("Send .help in any chat (that you can type in) to see available commands.")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
