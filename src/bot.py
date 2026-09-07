# ----------------------------------------------------------------------------------
# brief : Define the bot honeypot
# author : l.heywang
# date : 07/09/2026
# ----------------------------------------------------------------------------------

# Imports
from datetime import datetime, timedelta, timezone
import os
import discord
from discord.ext import commands

# Fetch the systems config (defined by systemd)
TOKEN = os.getenv("DISCORD_TOKEN")
HONEYPOT_CHANNEL_ID = int(os.getenv("HONEYPOT_CHANNEL_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

# Default intents (nothing to do on the discord portal)
intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    print(f"[INFO] Honeypot started on {HONEYPOT_CHANNEL_ID}.")


@client.event
async def on_message(message: discord.Message) -> None:

    # First, filter the message
    if message.channel.id != HONEYPOT_CHANNEL_ID or message.author.bot:
        return
    member = message.author
    if not isinstance(member, discord.Member):
        return

    # Then, delete the trigger message
    try:
        await message.delete()
    except discord.HTTPException:
        print("[WARN] Failed to delete the trigger message.")
        pass

    # Now, timeout the member
    timeout_duration = timedelta(days=7)
    timeout_success = False

    try:
        await member.timeout(
            timeout_duration,
            reason="[Honeypot] Tu penseras à changer ton mot de passe :)",
        )
        timeout_success = True
    except discord.Forbidden:
        print(f"[ERROR] Permissions to low to timeout : {member} ({member.id}).")
    except discord.HTTPException as err:
        print(f"[ERREUR] Failed to apply the timeout {err}")

    # Finally, notify the moderation team
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel and isinstance(log_channel, discord.TextChannel):
        created_ts = int(member.created_at.timestamp())
        embed = discord.Embed(
            title="🪤 Honeypot : Triggered",
            color=0x2ECC71 if timeout_success else 0xE74C3C,
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_author(
            name=f"{member} ({member.id})",
            icon_url=member.display_avatar.url,
        )
        embed.add_field(
            name="Status",
            value=(
                "⏳ Timed-out (7 days)"
                if timeout_success
                else "⚠️ Failed. Check the permissions."
            ),
            inline=True,
        )
        embed.add_field(
            name="Compte age :",
            value=f"<t:{created_ts}:R>",
            inline=True,
        )

        await log_channel.send(embed=embed)


if __name__ == "__main__":
    if not TOKEN or not HONEYPOT_CHANNEL_ID or not LOG_CHANNEL_ID:
        raise ValueError(
            "Missing env variables (TOKEN, HONEYPOT_CHANNEL_ID, LOG_CHANNEL_ID)."
        )
    client.run(TOKEN)
