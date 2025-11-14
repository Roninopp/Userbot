import os
import importlib
import logging
import sys  # <-- We've added this import
from telethon import TelegramClient, events

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
SESSION_NAME = "my_userbot"

if not API_ID:
    API_ID = input("Please enter your API ID: ")
if not API_HASH:
    API_HASH = input("Please enter your API HASH: ")

# This dictionary will hold help messages for loaded plugins
PLUGINS = {}
PLUGIN_PATH = "plugins"

# --- NEW PLUGIN LOADER ---
# Add the plugin path to the system path so importlib can find it
# This is the main change
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
                # We now use import_module, which is a different method
                module = importlib.import_module(plugin_name)
                
                # Check for the 'register' function and call it
                if hasattr(module, 'register'):
                    module.register(client, PLUGINS)
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} has no 'register' function.")
            except Exception as e:
                # Log the full traceback for better debugging
                logger.error(f"Failed to load plugin {plugin_name}:", exc_info=True)
# --- END OF NEW LOADER ---

# Initialize the client
client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

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
    
    load_plugins() # Load all plugins after client is started
    
    me = await client.get_me()
    logger.info(f"Userbot started successfully as {me.first_name} (@{me.username})!")
    logger.info("Send .help in any chat (that you can type in) to see available commands.")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
