from telethon import events
import asyncio # We need this for sleeping

# --- Plugin Functions ---

@events.register(events.NewMessage(pattern=r'\.countdown (\d+)', outgoing=True))
async def countdown(event):
    """Performs a countdown from the given number."""
    try:
        # Get the number from the command, e.g., ".countdown 5"
        number = int(event.pattern_match.group(1))
        
        # Don't allow huge numbers
        if number > 20:
            await event.edit("`Number is too big! (Max 20)`")
            return
            
        # Perform the countdown
        for i in range(number, 0, -1):
            await event.edit(f"**{i}**")
            await asyncio.sleep(1)
            
        await event.edit("**BOOM!** 💥")
        
    except Exception as e:
        await event.edit(f"`Error: {e}`")

@events.register(events.NewMessage(pattern=r'\.lame (.*)', outgoing=True))
async def lame_text(event):
    """Converts your text into lAmE tExT."""
    text_to_lame = event.pattern_match.group(1)
    if not text_to_lame:
        await event.edit("`Usage: .lame <text>`")
        return

    lame = ""
    for i, char in enumerate(text_to_lame):
        if i % 2 == 0:
            lame += char.upper()
        else:
            lame += char.lower()
            
    await event.edit(lame)

# --- Plugin Registration ---
# This is the most important part!
def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    # Add our new event handlers to the bot
    client.add_event_handler(countdown)
    client.add_event_handler(lame_text)
    
    # Add this plugin's help message
    help_dict['Extra Fun'] = (
        "`.countdown <number>`: Performs a countdown.\n"
        "`.lame <text>`: Converts your text to aLtErNaTiNg cApS."
    )
