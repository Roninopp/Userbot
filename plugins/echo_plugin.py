from telethon import events
import json
import os
import time

# --- Config ---
ECHO_TARGET_FILE = "echo_target.json"
# Cooldown in seconds to prevent flood bans
ECHO_COOLDOWN = 2 

# This variable will hold the last time an echo was sent
last_echo_time = 0

# --- Command to ADD the echo target ---
@events.register(events.NewMessage(pattern=r'\.addecho', outgoing=True))
async def add_echo(event):
    """Starts echoing the replied-to user."""
    
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.edit("`Reply to a user to start echoing them.`")
        return

    try:
        target_user = await reply_msg.get_sender()
        target_id = target_user.id
        
        # Save the target's ID to our file
        with open(ECHO_TARGET_FILE, "w", encoding="utf-8") as f:
            json.dump({"target_id": target_id})
            
        await event.edit(f"`Successfully started echoing:` **{target_user.first_name}**")

    except Exception as e:
        await event.edit(f"**Echo Add Error:**\n`{e}`")


# --- Command to REMOVE the echo target ---
@events.register(events.NewMessage(pattern=r'\.rmecho', outgoing=True))
async def remove_echo(event):
    """Stops echoing the user."""
    
    if os.path.exists(ECHO_TARGET_FILE):
        os.remove(ECHO_TARGET_FILE)
        await event.edit("`Echoing has been stopped.`")
    else:
        await event.edit("`No echo target is currently set.`")


# --- The Main Echo Handler ---
# This function will run on EVERY new incoming message
async def echo_message_handler(event):
    """Checks incoming messages and echoes the target if conditions are met."""
    
    global last_echo_time # Use the global variable for cooldown
    
    # 1. Check if we have a target file
    if not os.path.exists(ECHO_TARGET_FILE):
        return

    # 2. Check if the message is from a group (safety)
    if not event.is_group:
        return
        
    # 3. Check Cooldown (SAFETY)
    current_time = time.time()
    if (current_time - last_echo_time) < ECHO_COOLDOWN:
        return # Still in cooldown, do nothing

    try:
        # 4. Load the target ID
        with open(ECHO_TARGET_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        target_id = data.get("target_id")
        if not target_id:
            return
            
        # 5. Check if the message sender is our target
        if event.sender_id == target_id:
            # IT'S A MATCH! Echo the message.
            
            # Update the cooldown timer BEFORE sending
            last_echo_time = time.time()
            
            # Send the message
            # We use event.reply(event.message) to send the message
            # to the same chat where the target sent it.
            await event.reply(event.message)

    except Exception:
        # If something breaks (like file deleted mid-read), just ignore it
        pass


# --- Plugin Registration ---
def register(client, help_dict):
    """Registers all handlers for the echo plugin."""
    
    # Register the .addecho and .rmecho commands
    client.add_event_handler(add_echo)
    client.add_event_handler(remove_echo)
    
    # Register the main echo_message_handler
    # This one is different: it listens for ALL incoming messages
    client.add_event_handler(echo_message_handler, events.NewMessage(incoming=True))
    
    # Add help text
    help_dict['Echo'] = (
        "`.addecho` (reply to user):\n"
        "    Starts echoing their messages in groups (with a 3s cooldown).\n"
        "`.rmecho`:\n"
        "    Stops echoing."
    )
