import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

giveaways = {}

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

    giveaways[message.id] = {
        "prize": prize,
        "channel": ctx.channel.id
    }

    await ctx.send(f"Giveaway lancé pour **{prize}**")

    await discord.utils.sleep_until(
        discord.utils.utcnow() + discord.timedelta(seconds=duration)
    )

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
        await ctx.send(f"🎉 Félicitations {winner.mention} ! Tu as gagné **{prize}**")

bot.run(os.getenv("TOKEN"))
