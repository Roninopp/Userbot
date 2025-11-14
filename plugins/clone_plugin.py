from telethon import events
from telethon.tl import functions
import json
import os
import asyncio

# --- Config ---
# This is the file where your original profile will be backed up
BACKUP_FILE = "profile_backup.json"
# Temporary file names for photo downloads
CLONED_PHOTO_FILE = "cloned_dp.jpg"
ORIGINAL_PHOTO_FILE = "original_dp.jpg"

# --- Clone Command ---
@events.register(events.NewMessage(pattern=r'\.clone', outgoing=True))
async def clone_profile(event):
    """Clones the replied user's profile (Name, Bio, Photo)."""
    
    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.edit("`Reply to a user's message to clone them.`")
        return

    try:
        await event.edit("`Cloning... Step 1/3: Backing up current profile...`")

        # 1. Get target user and ourself ("me")
        target_user = await reply_msg.get_sender()
        me = await event.client.get_me()

        # 2. Get full user info (which includes the bio)
        target_full = await event.client(functions.users.GetFullUserRequest(target_user.id))
        my_full = await event.client(functions.users.GetFullUserRequest(me.id))

        # 3. Save our current profile to the backup file
        my_bio = my_full.full_user.about or ""
        my_photo_path = await event.client.download_profile_photo(me, file=ORIGINAL_PHOTO_FILE)

        backup_data = {
            "first_name": me.first_name,
            "last_name": me.last_name or "",
            "bio": my_bio,
            "photo_path": my_photo_path # This will be None if no photo
        }

        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup_data, f)

        await event.edit("`Cloning... Step 2/3: Applying new profile...`")

        # 4. Download the target's profile photo
        # We only download the first (current) photo
        cloned_photo_path = await event.client.download_profile_photo(
            target_user, 
            file=CLONED_PHOTO_FILE, 
            download_big=True # Get the best quality
        )
        
        # 5. Update our profile picture (if they have one)
        if cloned_photo_path:
            uploaded_file = await event.client.upload_file(cloned_photo_path)
            await event.client(functions.photos.UploadProfilePhotoRequest(uploaded_file))
            os.remove(cloned_photo_path) # Clean up the downloaded file

        # 6. Update our name and bio
        target_bio = target_full.full_user.about or ""
        await event.client(functions.account.UpdateProfileRequest(
            first_name=target_user.first_name,
            last_name=target_user.last_name or "",
            about=target_bio
        ))
        
        await event.edit(f"✅ **Successfully cloned:** `{target_user.first_name}`")

    except Exception as e:
        await event.edit(f"**Clone Error:**\n`{e}`")
        # Clean up temp files on error
        if os.path.exists(CLONED_PHOTO_FILE):
            os.remove(CLONED_PHOTO_FILE)


# --- Revert Command ---
@events.register(events.NewMessage(pattern=r'\.revert', outgoing=True))
async def revert_profile(event):
    """Reverts your profile to the state before .clone was used."""
    
    if not os.path.exists(BACKUP_FILE):
        await event.edit("`No backup file found. Cannot revert.`")
        return

    await event.edit("`Reverting profile...`")

    try:
        # 1. Load the backup data
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            backup_data = json.load(f)

        # 2. Revert name and bio
        await event.client(functions.account.UpdateProfileRequest(
            first_name=backup_data.get("first_name", ""),
            last_name=backup_data.get("last_name", ""),
            about=backup_data.get("bio", "")
        ))

        # 3. Delete all current profile photos
        # This prepares for uploading the original (or setting no photo)
        current_photos = await event.client.get_profile_photos('me')
        if current_photos:
            await event.client(functions.photos.DeletePhotosRequest(current_photos))

        # 4. Revert profile photo (if one was backed up)
        original_photo = backup_data.get("photo_path")
        if original_photo and os.path.exists(original_photo):
            uploaded_file = await event.client.upload_file(original_photo)
            await event.client(functions.photos.UploadProfilePhotoRequest(uploaded_file))
            os.remove(original_photo) # Clean up the original photo file

        # 5. Clean up the backup file itself
        os.remove(BACKUP_FILE)

        await event.edit("✅ **Profile successfully reverted!**")

    except Exception as e:
        await event.edit(f"**Revert Error:**\n`{e}`")


# --- Plugin Registration ---
def register(client, help_dict):
    """Registers the plugin's handlers and help message."""
    
    client.add_event_handler(clone_profile)
    client.add_event_handler(revert_profile)
    
    help_dict['Clone'] = (
        "`.clone` (reply to user):\n"
        "    Clones their Name, Bio, and DP. Saves your old profile.\n"
        "`.revert`:\n"
        "    Restores your profile from the last backup."
    )
