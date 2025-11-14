import asyncio
from telethon.sync import functions, types
from telethon import events

# WARNING: This is a DANGEROUS command.
# It will attempt to ban every single member from a chat.
# Only use this in chats YOU OWN and for testing purposes.
# We are not responsible for any damage, banned accounts, or lost group members.

@borg.on(events.NewMessage(pattern=r"\.banall", outgoing=True))
async def ban_all_members(event):
    if not event.is_group and not event.is_channel:
        await event.edit("`This command only works in groups and channels.`")
        return

    try:
        # 1. Get the chat
        chat = await event.get_chat()
        chat_id = event.chat_id

        # 2. Check if YOU have ban permissions
        me = await event.client.get_me()
        perms = await event.client.get_permissions(chat_id, me)
        
        if not perms.ban_users:
            await event.edit("`I don't have permission to ban users in this chat.`")
            return

        await event.edit(f"`Initiating .banall sequence in {chat.title}...`")
        await asyncio.sleep(2)
        
        # 3. Get all participants
        # We fetch participants in batches
        all_participants = []
        async for user in event.client.iter_participants(chat_id):
            all_participants.append(user)

        await event.edit(f"`Found {len(all_participants)} members. Commencing ban...`")
        
        count = 0
        total = len(all_participants)
        
        # 4. Loop and ban
        for user in all_participants:
            # Don't ban yourself or the chat creator/admins if possible
            # (Though getting all admins first is more robust)
            if user.id == me.id:
                continue

            try:
                # The core ban logic
                await event.client(functions.channels.EditBannedRequest(
                    chat_id,
                    user.id,
                    types.ChannelBannedRights(
                        until_date=None,  # Forever
                        view_messages=True # Ban them
                    )
                ))
                
                count += 1
                
                # Add a sleep to avoid hitting Telegram's API limits (FloodWaitError)
                if count % 20 == 0: # Every 20 bans, update and sleep
                    await event.edit(f"`Banned {count}/{total} users...`")
                    await asyncio.sleep(5) # Sleep for 5 seconds

            except Exception as e:
                # This will often fail on other admins or the owner
                print(f"Failed to ban {user.first_name}: {e}")
                pass
        
        await event.edit(f"**Ban sequence complete!**\n`Banned {count} / {total} members.`")

    except Exception as e:
        await event.edit(f"**An error occurred:**\n`{str(e)}`")

# You might need to add this line at the end if your bot requires it
# print("BanAll Plugin Loaded.")
