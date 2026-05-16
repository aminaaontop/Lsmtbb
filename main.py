import discord
from discord.ext import commands
import random

TOKEN = "TON_TOKEN_ICI"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

giveaways = {}

@bot.event
async def on_ready():
    print(f"Connecté : {bot.user}")

# CREATE GIVEAWAY
@bot.command()
async def gcreate(ctx, *, prize):

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"Réagis avec 🎉 pour participer\n\n🏆 {prize}",
        color=0x00ff00
    )

    msg = await ctx.send(embed=embed)

    await msg.add_reaction("🎉")

    giveaways[msg.id] = prize

    await ctx.send(f"✅ Giveaway créé\nID: {msg.id}")

# END GIVEAWAY
@bot.command()
async def gend(ctx, message_id: int):

    try:
        msg = await ctx.channel.fetch_message(message_id)

        reaction = discord.utils.get(msg.reactions, emoji="🎉")

        users = [user async for user in reaction.users()]

        users.remove(bot.user)

        if len(users) == 0:
            await ctx.send("❌ Aucun participant")
            return

        winner = random.choice(users)

        await ctx.send(f"🏆 Gagnant : {winner.mention}")

    except:
        await ctx.send("❌ Giveaway introuvable")

# SET WINNER
@bot.command()
async def gwinner(ctx, member: discord.Member):

    await ctx.send(f"🏆 Nouveau gagnant : {member.mention}")

# FIND USER
@bot.command()
async def find(ctx, member: discord.Member):

    voice = member.voice

    if voice is None:
        await ctx.send("❌ Pas en vocal")
        return

    await ctx.send(
        f"""
🎤 Salon : {voice.channel.name}

🔇 Mute : {voice.mute}

🎧 Deaf : {voice.deaf}
"""
    )

# RENEW
@bot.command()
async def renew(ctx):

    await ctx.send("♻️ Giveaway renouvelé")

bot.run(TOKEN)
