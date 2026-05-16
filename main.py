import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import random
import os
import asyncio

# ---------------- WEB SERVER ----------------

app = Flask('')

@app.route('/')
def home():
    return "Bot online"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- DISCORD BOT ----------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

giveaways = {}

# ---------------- EVENTS ----------------

@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")

# ---------------- PING ----------------

@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓")

# ---------------- GIVEAWAY ----------------

@bot.command()
async def giveaway(ctx, duration: int, *, prize):

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=(
            f"Réagis avec 🎉 pour participer !\n\n"
            f"🏆 Prix : **{prize}**\n"
            f"⏳ Durée : **{duration} secondes**"
        ),
        color=0xff0000
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")

    giveaways[message.id] = {
        "prize": prize,
        "ended": False,
        "channel_id": ctx.channel.id
    }

    await ctx.send(f"🎉 Giveaway lancé pour **{prize}**")

    await asyncio.sleep(duration)

    if giveaways[message.id]["ended"]:
        return

    await end_giveaway(ctx.channel, message.id)

# ---------------- END FUNCTION ----------------

async def end_giveaway(channel, message_id):

    try:
        message = await channel.fetch_message(message_id)
    except:
        return

    users = []

    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)

    giveaways[message_id]["ended"] = True

    if len(users) == 0:
        await channel.send("😢 Personne n'a participé.")
    else:
        winner = random.choice(users)

        embed = discord.Embed(
            title="🎉 GIVEAWAY TERMINÉ",
            description=f"🏆 Gagnant : {winner.mention}",
            color=0x57F287
        )

        embed.add_field(
            name="🎁 Prix",
            value=giveaways[message_id]["prize"],
            inline=False
        )

        await channel.send(embed=embed)

# ---------------- FIND ----------------

@bot.command()
async def find(ctx, message_id: int):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    data = giveaways[message_id]

    embed = discord.Embed(
        title="🔎 Giveaway trouvé",
        description=f"ID : `{message_id}`",
        color=0x5865F2
    )

    embed.add_field(
        name="🎁 Prix",
        value=data["prize"],
        inline=False
    )

    embed.add_field(
        name="📢 Salon",
        value=ctx.channel.mention,
        inline=False
    )

    embed.add_field(
        name="⛔ Terminé",
        value=str(data["ended"]),
        inline=False
    )

    embed.set_footer(text="Système Giveaway")

    await ctx.send(embed=embed)

# ---------------- ENDGW ----------------

@bot.command()
async def endgw(ctx, message_id: int):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    if giveaways[message_id]["ended"]:
        await ctx.send("⛔ Giveaway déjà terminé.")
        return

    giveaways[message_id]["ended"] = True

    await end_giveaway(ctx.channel, message_id)

# ---------------- REROLL ----------------

@bot.command()
async def reroll(ctx, message_id: int):

    try:
        message = await ctx.channel.fetch_message(message_id)
    except:
        await ctx.send("❌ Message introuvable.")
        return

    users = []

    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)

    if len(users) == 0:
        await ctx.send("❌ Aucun participant.")
    else:
        winner = random.choice(users)

        embed = discord.Embed(
            title="🔄 Nouveau gagnant",
            description=f"{winner.mention}",
            color=0xFEE75C
        )

        await ctx.send(embed=embed)

# ---------------- SETWINNER ----------------

@bot.command()
async def setwinner(ctx, message_id: int, member: discord.Member):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    embed = discord.Embed(
        title="👑 Gagnant défini",
        description=f"{member.mention}",
        color=0xED4245
    )

    embed.add_field(
        name="🎁 Prix",
        value=giveaways[message_id]["prize"],
        inline=False
    )

    await ctx.send(embed=embed)

# ---------------- DELETEGW ----------------

@bot.command()
async def deletegw(ctx, message_id: int):

    if message_id in giveaways:
        del giveaways[message_id]
        await ctx.send("🗑 Giveaway supprimé.")
    else:
        await ctx.send("❌ Giveaway introuvable.")

# ---------------- GWS ----------------

@bot.command()
async def gws(ctx):

    if len(giveaways) == 0:
        await ctx.send("❌ Aucun giveaway actif.")
        return

    embed = discord.Embed(
        title="📋 Giveaways actifs",
        color=0x5865F2
    )

    for gid, data in giveaways.items():

        embed.add_field(
            name=f"ID : {gid}",
            value=(
                f"🎁 Prize : {data['prize']}\n"
                f"⛔ Ended : {data['ended']}"
            ),
            inline=False
        )

    await ctx.send(embed=embed)

# ---------------- RENEW ----------------

@bot.command()
async def renew(ctx, message_id: int):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    data = giveaways[message_id]

    embed = discord.Embed(
        title="♻️ GIVEAWAY RELANCÉ",
        description="Réagis avec 🎉 pour participer !",
        color=0x57F287
    )

    embed.add_field(
        name="🎁 Prix",
        value=data["prize"],
        inline=False
    )

    new_message = await ctx.send(embed=embed)

    await new_message.add_reaction("🎉")

    giveaways[new_message.id] = {
        "prize": data["prize"],
        "ended": False,
        "channel_id": ctx.channel.id
    }

    await ctx.send(
        f"♻️ Giveaway relancé dans {ctx.channel.mention}"
    )

# ---------------- START ----------------

keep_alive()

bot.run(os.getenv("TOKEN"))        )
    else:
        await ctx.send("❌ Giveaway introuvable.")

# ----- ENDGW -----

@bot.command()
async def endgw(ctx, message_id: int):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    if giveaways[message_id]["ended"]:
        await ctx.send("⛔ Giveaway déjà terminé.")
        return

    giveaways[message_id]["ended"] = True

    await end_giveaway(ctx.channel, message_id)

# ----- REROLL -----

@bot.command()
async def reroll(ctx, message_id: int):

    try:
        message = await ctx.channel.fetch_message(message_id)
    except:
        await ctx.send("❌ Message introuvable.")
        return

    users = []

    for reaction in message.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)

    if len(users) == 0:
        await ctx.send("❌ Aucun participant.")
    else:
        winner = random.choice(users)
        await ctx.send(f"🔄 Nouveau gagnant : {winner.mention}")

# ----- SETWINNER -----

@bot.command()
async def setwinner(ctx, message_id: int, member: discord.Member):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    await ctx.send(
        f"👑 {member.mention} gagne **{giveaways[message_id]['prize']}**"
    )

# ----- DELETEGW -----

@bot.command()
async def deletegw(ctx, message_id: int):

    if message_id in giveaways:
        del giveaways[message_id]
        await ctx.send("🗑 Giveaway supprimé.")
    else:
        await ctx.send("❌ Giveaway introuvable.")

# ----- GWS -----

@bot.command()
async def gws(ctx):

    if len(giveaways) == 0:
        await ctx.send("❌ Aucun giveaway actif.")
        return

    text = ""

    for gid, data in giveaways.items():
        text += (
            f"ID: {gid} | "
            f"Prize: {data['prize']} | "
            f"Ended: {data['ended']}\n"
        )

    await ctx.send(f"```{text}```")

# ----- RENEW -----

@bot.command()
async def renew(ctx, message_id: int):

    if message_id not in giveaways:
        await ctx.send("❌ Giveaway introuvable.")
        return

    data = giveaways[message_id]

    embed = discord.Embed(
        title="🎉 GIVEAWAY RELANCÉ 🎉",
        description=f"Réagis avec 🎉 pour participer !\n\n🏆 Prix : **{data['prize']}**",
        color=0x00ff00
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")

    giveaways[message.id] = {
        "prize": data["prize"],
        "ended": False,
        "channel_id": ctx.channel.id
    }

    await ctx.send("♻️ Giveaway relancé.")

# ----- LANCEMENT -----

keep_alive()

bot.run(os.getenv("TOKEN"))
