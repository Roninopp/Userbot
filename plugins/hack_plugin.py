from telethon import events
import asyncio
import random

# --- Helper Function to Get Target ---
async def get_target_display_name(event):
    """Gets a display name for the target of the .hack command."""
    
    # Check if a username/text is provided after .hack
    target_text = event.pattern_match.group(1).strip()
    if target_text:
        return target_text # e.g., "@username" or "the server"

    # Check if replying to a message
    # --- THIS IS THE FIXED LINE ---
    reply_msg = await event.get_reply_message()
    # --- END OF FIX ---
    
    if reply_msg:
        try:
            # Get the user who sent the message
            user = await reply_msg.get_sender()
            if user.first_name:
                # Use their first name
                return user.first_name
        except Exception:
            # Fallback for channels or deleted users
            return "target"
            
    # If no target, return None
    return None

# --- Main Hacking Animation ---

@events.register(events.NewMessage(pattern=r'\.hack(.*)', outgoing=True))
async def hack_animation(event):
    """Runs a fake, cinematic hacking animation."""
    
    target_name = await get_target_display_name(event)
    
    if not target_name:
        await event.edit("`Usage: .hack <target>` or reply to a user's message.")
        return

    # A list of all the "frames" of our animation
    animation_frames = [
        f"█ 10% | Connecting to {target_name}'s mainframe...",
        f"██ 20% | Bypassing firewall... `[OK]`",
        f"███ 30% | Locating IP address... `[FOUND]`",
        f"████ 40% | IP: `192.168.{random.randint(0, 255)}.{random.randint(0, 255)}`", # Fake IP
        f"█████ 50% | Attempting SSH bruteforce...",
        f"██████ 60% | SSH connection established. `[OK]`",
        f"███████ 70% | Injecting payload: `keylogger.exe`",
        f"████████ 80% | Gaining root access... `[GRANTED]`",
        f"█████████ 90% | Downloading files: `passwords.txt`, `user_data.db`",
        f"██████████ 100% | **HACK SUCCESSFUL**",
        f"**Target:** `{target_name}`\n**Status:** `COMPROMISED`\n\n`Initiating data transfer...`"
    ]

    # Loop through each frame and edit the message
    try:
        current_frame = ""
        for frame in animation_frames:
            # Add a small "typing" effect to each line
            current_frame += f"► {frame}\n"
            await event.edit(f"```\n{current_frame}\n```")
            await asyncio.sleep(1.5) # Safe delay to avoid flood wait

        # Final message after the loop
        await asyncio.sleep(2)
        await event.edit(f"✅ **Target `{target_name}` has been successfully hacked.**\n(Found User Adress And Mail Failed To Generate Contact Number)")

    except Exception as e:
        # Failsafe in case something goes wrong
        await event.edit(f"Animation failed: {e}")


# --- Plugin Registration ---
def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    # Add our new event handler
    client.add_event_handler(hack_animation)
    
    # Add this plugin's help message
    help_dict['Hack'] = (
        "`.hack <target>` or reply to a user:\n"
        "    Shows a cool (and fake) hacking animation."
    )
