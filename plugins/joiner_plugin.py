from telethon import events
from telethon.tl import functions
from telethon.tl.types import Channel
from telethon.errors.rpcerrorlist import FloodWaitError, UserAlreadyParticipantError
import asyncio

@events.register(events.NewMessage(pattern=r'\.join (.*)', outgoing=True))
async def join_groups(event):
    """Searches for and joins the top 5 groups matching the query."""
    
    query = event.pattern_match.group(1)
    if not query:
        await event.edit("`Usage: .join <search query>`")
        return

    await event.edit(f"`Searching for public groups matching '{query}'...`")
    
    try:
        # 1. Search for the query
        results = await event.client(functions.contacts.SearchRequest(
            q=query,
            limit=10  # Get 10 results to have a better chance of finding 5 groups
        ))
        
        # 2. Filter for actual supergroups (not channels, users, or bots)
        public_groups = []
        for chat in results.chats:
            if (isinstance(chat, Channel) and 
               (chat.megagroup or chat.gigagroup) and 
               not chat.broadcast): # Make sure it's a group, not a channel
                public_groups.append(chat)
            
            if len(public_groups) == 5:
                break # We only want to join 5

        if not public_groups:
            await event.edit(f"`No public groups (only channels/users) found for '{query}'.`")
            return

        await event.edit(f"`Found {len(public_groups)} groups. Attempting to join with a 30s delay...`")
        await asyncio.sleep(3) # Time to read the message

        joined_count = 0
        output_message = "--- **Join Results** ---\n\n"

        # 3. Loop and try to join EACH group with a long delay
        for i, group in enumerate(public_groups):
            
            # THIS IS THE MOST IMPORTANT PART FOR SAFETY
            if i > 0:
                await event.edit(f"`Waiting 30 seconds to avoid flood limits... ({i+1}/{len(public_groups)})`")
                await asyncio.sleep(30) # 30-second safety delay

            try:
                await event.edit(f"`({i+1}/{len(public_groups)}) Attempting to join {group.title}...`")
                await event.client(functions.channels.JoinChannelRequest(group))
                output_message += f"✅ **Joined:** {group.title}\n"
                joined_count += 1
            
            except UserAlreadyParticipantError:
                output_message += f"⚪ **Already in:** {group.title}\n"
            
            except FloodWaitError as e:
                await event.edit(f"**FLOOD WAIT ERROR!** Stopping. Please wait {e.seconds}s before trying again.")
                return # Stop immediately
            
            except Exception as e:
                # Catch other errors like "Chat full", "Banned", "Privacy settings"
                output_message += f"❌ **Failed to join {group.title}:** `{e}`\n"
        
        # 4. Final Report
        output_message += f"\n**Finished. Joined {joined_count}/{len(public_groups)} new groups.**"
        await event.edit(output_message)

    except Exception as e:
        await event.edit(f"**Search Error:** `{e}`")

# --- Plugin Registration ---
def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    client.add_event_handler(join_groups)
    
    help_dict['Group Joiner'] = (
        "`.join <query>`:\n"
        "    Searches and joins the top 5 public groups. **USE WITH CAUTION.**"
    )
