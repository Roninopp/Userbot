import asyncio
from telethon import events

# ==========================================
# 1. .terminal - Fake Hacker Animation
# ==========================================
@borg.on(events.NewMessage(pattern=r"\.terminal", outgoing=True))
async def terminal_animation(event):
    # The animation frames
    animation_frames = [
        "```Initializing...```",
        "```Loading Modules... [10%]```",
        "```Loading Modules... [35%]```",
        "```Loading Modules... [89%]```",
        "```Modules Loaded.```",
        "```> Accessing Mainframe...```",
        "```> Bypassing Firewalls...```",
        "```> Firewalls Bypassed.```",
        "```> Downloading Database...```",
        "```> [||||||||||     ] 60%```",
        "```> [|||||||||||||||] 100%```",
        "```> Decrypting Passwords...```",
        "```> ACCESS GRANTED```",
        "**💀 SYSTEM HACKED 💀**"
    ]

    for frame in animation_frames:
        await event.edit(frame)
        await asyncio.sleep(0.5) # Speed of animation

# ==========================================
# 2. .police - Siren Animation
# ==========================================
@borg.on(events.NewMessage(pattern=r"\.police", outgoing=True))
async def police_animation(event):
    await event.edit("🚨 **POLICE ASSAULT IN PROGRESS** 🚨")
    await asyncio.sleep(1)
    
    # Loop the siren lights
    for i in range(10): # Loops 10 times
        await event.edit("🔴 ⚪️ 🔴 ⚪️ 🔴 ⚪️")
        await asyncio.sleep(0.3)
        await event.edit("⚪️ 🔵 ⚪️ 🔵 ⚪️ 🔵")
        await asyncio.sleep(0.3)
    
    await event.edit("👮 **WEE WOO WEE WOO** 👮")

# ==========================================
# 3. .moon - Moon Phase Animation
# ==========================================
@borg.on(events.NewMessage(pattern=r"\.moon", outgoing=True))
async def moon_animation(event):
    phases = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    
    await event.edit("Look at the sky...")
    await asyncio.sleep(1)
    
    # Loop through phases 3 times
    for _ in range(3):
        for phase in phases:
            await event.edit(f"**The Moon:** {phase}")
            await asyncio.sleep(0.2)
            
    await event.edit("**The Moon is Beautiful tonight.** 🌕")

# ==========================================
# 4. .loading - Funny Loading Bar
# ==========================================
@borg.on(events.NewMessage(pattern=r"\.loading", outgoing=True))
async def loading_animation(event):
    await event.edit("⚡ **Initiating Download...**")
    await asyncio.sleep(1)
    
    percentage = 0
    while percentage < 100:
        # Fake random jumps in progress
        percentage += 10
        if percentage > 100: percentage = 100
        
        # Create a visual bar
        filled = "█" * (percentage // 10)
        empty = "░" * (10 - (percentage // 10))
        
        await event.edit(f"**Downloading Internet:**\n`[{filled}{empty}] {percentage}%`")
        await asyncio.sleep(0.5)
        
        # Add a funny "stuck" moment at 90%
        if percentage == 90:
            await event.edit(f"**Downloading Internet:**\n`[{filled}{empty}] 99%`\n*(Stuck...)*")
            await asyncio.sleep(2)
            
    await event.edit("**✅ Download Complete! You now own the internet.**")
