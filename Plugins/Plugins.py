from telethon import events
import time

# --- Plugin Functions ---

@events.register(events.NewMessage(pattern=r'\.ping', outgoing=True))
async def ping(event):
    """Responds with Pong! and the response time."""
    start_time = time.monotonic()
    await event.edit("Pong!")
    end_time = time.monotonic()
    response_time = (end_time - start_time) * 1000  # in milliseconds
    await event.edit(f"**Pong!**\n`{response_time:.2f} ms`")

@events.register(events.NewMessage(pattern=r'\.shrug', outgoing=True))
async def shrug(event):
    """Sends the classic shrug emoji."""
    await event.edit(r"¯\_(ツ)_/¯")

@events.register(events.NewMessage(pattern=r'\.type (.*)', outgoing=True))
async def type_effect(event):
    """Simulates a typing effect for the given text."""
    text_to_type = event.pattern_match.group(1)
    if not text_to_type:
        await event.edit("`Usage: .type <text>`")
        return

    current_text = ""
    for char in text_to_type:
        current_text += char
        await event.edit(current_text)
        time.sleep(0.1) # Adjust speed as needed

# --- Plugin Registration ---

def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    # Add event handlers to the client
    client.add_event_handler(ping)
    client.add_event_handler(shrug)
    client.add_event_handler(type_effect)
    
    # Add this plugin's help message to the main help dictionary
    help_dict['Fun Plugin'] = (
        "`.ping`: Checks if the bot is alive and shows response time.\n"
        "`.shrug`: Sends the shrug kaomoji.\n"
        "`.type <text>`: Edits the message to simulate typing."
    )
