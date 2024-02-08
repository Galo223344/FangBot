# This program is free software and licensed under the GNU Affero General Public License verson 3 (AGPL)
# The AGPL can be found in the LICENSE file within this repository
# Alternatively, the AGPL can be found here: https://www.gnu.org/licenses/agpl-3.0.en.html

import os
import logging
import re
import csv
from datetime import timedelta
from random import randrange

import discord
from discord.ext import commands as dc

# Perform some configuration for our application.
botToken = os.getenv("TOKEN")
modChan = int(os.getenv("MOD_CHANNEL"))
maxPing = int(os.getenv("MAX_PING"))
maxEmoji = int(os.getenv("MAX_EMOJI"))
serverId = int(os.getenv("SERVER_ID"))
welcomePost = int(os.getenv("ROLES_POST"))
winghugId = int(os.getenv("WINGHUG_ID"))
intents = discord.Intents.all()
bot = dc.Bot(command_prefix="!", intents=intents)
logger = logging.getLogger('discord')

# Remove the built in help command so that we can define a custom help command.
bot.remove_command("help")

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is ready.")

@bot.event
async def on_member_join(member):
    modChannel = bot.get_channel(modChan)
    msg = f"User {member.name} has joined the server."
    logger.info(msg)
    await modChannel.send(msg)

@bot.event
async def on_member_remove(member):
    modChannel = bot.get_channel(modChan)
    msg=f"User {member.name} has left the server."
    logger.info(msg)
    await modChannel.send(msg)

@bot.event
async def on_member_ban(guild, user):
        modChannel = bot.get_channel(modChan)
        msg = f"User {user.name} has been banned."
        logger.info(msg)
        await modChannel.send(msg)

@bot.event
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    emojiPattern = re.compile("<:[\S]+:[\d]+>")
    msgEmoji = re.findall(emojiPattern, ctx.content)
    if len(ctx.raw_mentions) > maxPing:
        author = ctx.author
        await ctx.delete()
        await ctx.channel.send(f"{maxPing} mentions per post, {author.mention}.")
        logger.info(f"{author.name} was warned for mass pings.")
    elif len(msgEmoji) > maxEmoji:
        author = ctx.author
        await ctx.delete()
        await ctx.channel.send(f"{maxEmoji} emoji per post, {author.mention}.")
        logger.info(f"{author.name} was warned for mass emoji.")
    else:
        await bot.process_commands(ctx)

@bot.event
async def on_raw_reaction_add(payload):
    msg = payload.message_id
    uid = payload.user_id
    emoji = payload.emoji.name
    if msg == welcomePost:
        server = bot.get_guild(serverId)
        user = server.get_member(uid)
        with open('roles.csv', mode='r') as f:
            reader = csv.reader(f)
            rolelist = {r[0]:r[1] for r in reader}
            if emoji in rolelist:
                role = server.get_role(int(rolelist[emoji]))
                await user.add_roles(role)
                logger.info(f"{role.name} was added to {user.name}.")

@bot.event
async def on_raw_reaction_remove(payload):
    msg = payload.message_id
    uid = payload.user_id
    emoji = payload.emoji.name
    if msg == welcomePost:
        server = bot.get_guild(serverId)
        user = server.get_member(uid)
        with open('roles.csv', mode='r') as f:
            reader = csv.reader(f)
            rolelist = {r[0]:r[1] for r in reader}
            if emoji in rolelist:
                role = server.get_role(int(rolelist[emoji]))
                await user.remove_roles(role)
                logger.info(f"{role.name} was removed from {user.name}.")

@bot.command(name='stickers', help='List all stickers by name and ID.')
async def liststickers(ctx):
    message = ''
    for s in ctx.guild.stickers:
        message = message + f'Sticker name: {s.name} with ID: {s.id}\n'
    await ctx.reply(message)

@bot.command()
async def sneed(ctx):
    await ctx.send("What you s*need* are your meds, Anon.")
    member = ctx.author
    startingDelta = timedelta(days=1, minutes=1)
    totalSeconds = startingDelta.total_seconds()
    chosenSecondsAmount = randrange(1, totalSeconds)
    formattedChosenSecondsAmount = format(str(timedelta(seconds=chosenSecondsAmount)))
    logger.info(formattedChosenSecondsAmount)
    await member.timeout(startingDelta)

@bot.command(name="winghug")
async def winghug(ctx, *mentions:discord.Member):
    s = await bot.get_guild(serverId).fetch_sticker(winghugId)
    ref = ctx.message.reference
    if ref != None:
        m = await ctx.channel.fetch_message(ref.message_id)
        if m.author == bot.user:
            await ctx.reply("I don't need to hug myself, dweeb!")
        else:
            await ctx.send(stickers=[s], reference=ref)
    elif len(mentions) > 2:
        userlist = ' '.join([u.mention for u in mentions])
        await ctx.send(f'{userlist}', stickers=[s])
    else:
        await ctx.reply(stickers=[s])

@bot.command()
async def info(ctx):
    message = """
FangBot has been developed by
- BobCzar
- rc_05

Other developers will be added when needed.
The source code is available [here](https://github.com/BobCzar/FangBot).
"""
    await ctx.send(message)

@bot.command()
async def help(ctx):
    message = """
All commands must start with !
List of commands:
- sneed
    Sneed's Feed & Seed (Formerly Chuck's)
- winghug
    Send a user a winghug!
    Reply to a post to hug that user, or @ping users to hug them. Do neither and Fang will hug you.
- help
    This very message that you are seeing.
- info
    Extra info that you may or may not find interesting.
"""
    await ctx.send(message)

bot.run(botToken)
