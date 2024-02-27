# This program is free software and licensed under the GNU Affero General Public License verson 3 (AGPL)
# The AGPL can be found in the LICENSE file within this repository
# Alternatively, the AGPL can be found here: https://www.gnu.org/licenses/agpl-3.0.en.html

import os
import logging
import re
import csv
import random
from datetime import timedelta
from random import randrange
from dotenv import load_dotenv

import discord
from discord.ext import commands as dc

load_dotenv()

# Perform some configuration for our application.
botToken = os.getenv("TOKEN")
modChan = int(os.getenv("MOD_CHANNEL"))
modRole = int(os.getenv("MOD_ROLE"))
maxPing = int(os.getenv("MAX_PING"))
maxEmoji = int(os.getenv("MAX_EMOJI"))
serverId = int(os.getenv("SERVER_ID"))
welcomePost = int(os.getenv("ROLES_POST"))
winghugId = int(os.getenv("WINGHUG_ID"))
intents = discord.Intents(
    guilds=True,
    members=True,
    moderation=True,
    emojis_and_stickers=True,
    guild_messages=True,
    guild_reactions=True,
    message_content=True
)
bot = dc.Bot(command_prefix="!", intents=intents)
logger = logging.getLogger('discord')

# Remove the built in help command so that we can define a custom help command.
bot.remove_command("help")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, dc.CommandNotFound):
        return #silently ignore the user
    elif isinstance(error, dc.CommandOnCooldown):
        await ctx.reply(error)
    else:
        await ctx.reply(f"Unexpected error: {error}")

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} is ready.")

@bot.event
async def on_member_join(member):
    modChannel = bot.get_channel(modChan)
    embed = discord.Embed(
        description=f"📥{member.mention} has joined the server",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_author(name=member.name, icon_url=member.avatar.url)
    embed.add_field(name="User ID", value= member.id)
    embed.add_field(name="Account Creation", value=member.created_at.strftime("%Y-%m-%d, %H:%M"))
    await modChannel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    modChannel = bot.get_channel(modChan)
    embed = discord.Embed(
        description=f"📤{member.mention} has left the server",
        color=discord.Color.orange()
    )
    embed.set_thumbnail(url=member.avatar.url)
    embed.set_author(name=member.name, icon_url=member.avatar.url)
    embed.add_field(name="User ID", value= member.id)
    embed.add_field(name="Account Creation", value=member.created_at.strftime("%Y-%m-%d, %H:%M"))
    await modChannel.send(embed=embed)

@bot.event
async def on_member_ban(guild, user):
    modChannel = bot.get_channel(modChan)
    embed = discord.Embed(
        description=f"🔒{user.mention} has been banned from the server",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="User ID", value= user.id)
    embed.add_field(name="Account Creation", value=user.created_at.strftime("%Y-%m-%d, %H:%M"))
    await modChannel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):
    modChannel = bot.get_channel(modChan)
    embed = discord.Embed(
        description=f"🔓{user.mention} has been unbanned from the server",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_author(name=user.name, icon_url=user.avatar.url)
    embed.add_field(name="User ID", value= user.id)
    embed.add_field(name="Account Creation", value=user.created_at.strftime("%Y-%m-%d, %H:%M"))
    await modChannel.send(embed=embed)

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
        with open('roles.csv', mode='r', encoding='utf-8') as f:
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
        with open('roles.csv', mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rolelist = {r[0]:r[1] for r in reader}
            if emoji in rolelist:
                role = server.get_role(int(rolelist[emoji]))
                await user.remove_roles(role)
                logger.info(f"{role.name} was removed from {user.name}.")

@bot.command(name="snoot")
async def snoot(ctx):
    with open('snoot.txt', mode='r') as f:
            lines = f.read().splitlines()
            response = random.choice(lines)
            await ctx.send(response)
            await ctx.send("<:glorysnoot:870704286366040064>")

@bot.command(name="nuggie")
async def nuggie(ctx):
    with open('nuggie.txt', mode='r') as f:
            lines = f.read().splitlines()
            response = random.choice(lines)
            await ctx.send("<:dinonugget:870729745925562398>")
            await ctx.send(response)
            await ctx.send("<:fangnugdevour:936042789605613578>")

@dc.cooldown(rate=1, per=60, type=dc.BucketType.user)
@bot.command(name="tail")
async def tail(ctx):
    with open('tail.txt', mode='r') as f:
            winner = False
            lines = f.read().splitlines()
            if random.random() > 0.001:
                response = random.choice(lines[1:])
            else:
                winner = True
                response = lines[0]
            await ctx.send("<:fangsurprised:870685719528615968>")
            await ctx.send(response)
            if winner:
                logger.info(f"{ctx.author.name} won the tail roulette.")

@bot.command(name="sneed")
async def sneed(ctx):
    await ctx.send("What you s*need* are your meds, Anon.")
    member = ctx.author
    isJanny = member.get_role(modRole)
    if isJanny == None:
        startingDelta = timedelta(days=1, minutes=1)
        totalSeconds = startingDelta.total_seconds()
        chosenSecondsAmount = randrange(1, totalSeconds)
        timeoutDelta = timedelta(seconds=chosenSecondsAmount)
        formattedChosenSecondsAmount = format(str(timedelta(seconds=chosenSecondsAmount)))
        logger.info(f"{member} was timed out for {formattedChosenSecondsAmount} seconds")
        await member.timeout(timeoutDelta)

@bot.command(name="winghug")
async def winghug(ctx, *mentions:discord.Member):
    s = await bot.get_guild(serverId).fetch_sticker(winghugId)
    ref = ctx.message.reference
    if ref != None:
        m = await ctx.channel.fetch_message(ref.message_id)
        if m.author == bot.user:
            await ctx.reply("I'm not hugging myself, dweeb!")
        else:
            await ctx.send(stickers=[s], reference=ref)
    elif len(mentions) > 2:
        userlist = ' '.join([u.mention for u in mentions])
        await ctx.send(f'{userlist}', stickers=[s])
    else:
        await ctx.reply(stickers=[s])

@bot.command(name='stickers')
async def liststickers(ctx):
    if ctx.author.get_role(modRole) == None:
        return
    message = ''
    for s in ctx.guild.stickers:
        stickerinfo = f'{s.name}: {s.id}\n'
        if len(message) + len(stickerinfo) > 2000:
            await ctx.send(message)
            message = stickerinfo
        else:
            message += stickerinfo
    await ctx.send(message)

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
- snoot
    Boop that snoot!
- nuggie
    Give Fang a nuggie
- tail
    Don't let Ripley catch you
- sneed
    Sneed's Feed & Seed (Formerly Chuck's)
- winghug
    Send a user a winghug!
    Reply to a post to hug that user, or @ping users to hug them.
    Do neither and Fang will hug you.
- stickers
    Returns a list of all stickers on the server with their sticker IDs.
    Moderators only, since this is only for bot configuration.
- help
    This very message that you are seeing.
- info
    Extra info that you may or may not find interesting.
"""
    await ctx.send(message)

bot.run(botToken)
