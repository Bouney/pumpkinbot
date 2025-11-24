import discord
from discord.ext import commands
import logging
import os
import sys
from dotenv import load_dotenv

# 1. Import the web server for Render
from keep_alive import keep_alive 

# Load .env for local testing (Render ignores this and uses Dashboard Envs)
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2. Update Logging to print to Console (Best for Render Dashboard)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
secret_role = "Gamer"

@bot.event
async def on_ready():
    print(f"We are ready to go in as {bot.user.name} (ID: {bot.user.id})")

@bot.event
async def on_member_join(member):
    try:
        await member.send(f"Welcome to the server {member.name}")
    except discord.Forbidden:
        # This happens if the user has DMs blocked
        print(f"Could not DM {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "shit" in message.content.lower():
        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention} - dont use that word!")
        except discord.Forbidden:
            print("Bot lacks permission to delete messages.")
            
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        try:
            await ctx.author.add_roles(role)
            await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}")
        except discord.Forbidden:
            await ctx.send("I cannot assign that role! Please make sure my role is higher than the 'Gamer' role.")
    else:
        await ctx.send(f"Role '{secret_role}' doesn't exist.")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        try:
            await ctx.author.remove_roles(role)
            await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
        except discord.Forbidden:
             await ctx.send("I cannot remove that role! Check my permissions.")
    else:
        await ctx.send("Role doesn't exist")

@bot.command()
async def dm(ctx, *, msg):
    try:
        await ctx.author.send(f"You said: {msg}")
    except discord.Forbidden:
        await ctx.send("I can't DM you! Your DMs might be closed.")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question, color=0x00ff00)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("Welcome to the club!")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that!")

# 3. Start the Keep Alive server before running the bot
keep_alive()

if not token:
    print("Error: DISCORD_TOKEN not found. Set it in .env or Render Environment Variables.")
else:
    bot.run(token, log_handler=None) # We handled logging manually above
