import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import random
import os
import asyncio

# ----- Serveur web pour Render -----

app = Flask('')

@app.route('/')
def home():
    return "Bot online"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ----- Bot Discord -----

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté : {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong 🏓")

@bot.command()
async def giveaway(ctx, duration: int, *, prize):
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"Réagis avec 🎉 pour participer !\n\n🏆 Prix : **{prize}**\n⏳ Durée : **{duration} secondes**",
        color=0xff0000
    )

    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")

    await ctx.send(f"Giveaway lancé pour **{prize}**")

    await asyncio.sleep(duration)

    new_message = await ctx.channel.fetch_message(message.id)

    users = []

    for reaction in new_message.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)

    if len(users) == 0:
        await ctx.send("Personne n'a participé 😢")
    else:
        winner = random.choice(users)
        await ctx.send(f"🎉 {winner.mention} a gagné **{prize}** !")

keep_alive()

bot.run(os.getenv("TOKEN"))
