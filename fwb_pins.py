"""
FWB Pins - Community Curation ~ Airtable Functionality Removed ~
As users drop the ๐ emoji on valuable posts, the posts are archived in a review channel.

Written by Dexter Tortoriello // @houses for Friends With Benefits
"""

import logging
import os
from discord.ext import commands

# logging setup (I hate how much boilerplate this is!)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

client = commands.Bot(command_prefix = "!")

# Discord interaction params
## These are stored locally in a .env file which makes it easy to use `heroku local` for local dev
## รก la https://devcenter.heroku.com/articles/heroku-local#set-up-your-local-environment-variables
## For deployment, you'll need to add the env vars to your Heroku app,
## รก la https://devcenter.heroku.com/articles/config-vars#managing-config-vars

## The Discord bot token, from the Discord application Bot page
token = os.getenv("DISCORD_BOT_TOKEN")

## I'd really like all these params to be controlled by ! commands to the bot itself,
## Something like `!pin :some_emoji_here:` which would funnel posts with that react to that channel.
## But for now, we'll use env vars, because that's better than hard-coding, makes for easier Heroku deployment, 
## and doesn't require writing bot commands & maintaining state.

pin_channel_id = int(os.getenv("DISCORD_PIN_CHANNEL_ID"))
custom_emoji_ids = [int(s) for s in os.getenv("DISCORD_CUSTOM_EMOJI_IDS").split(",")]

## Set up the emoji we're using as triggers
pin_emoji = "๐" # That's U+1F4CC if you need to know
trigger_emojis = {pin_emoji} # We'll add to this set later, once we're connected

## Thresholds
trigger_react_req = 1 # Minimum total number of trigger reacts required to pin message
total_react_req = 15 # Minimum total number of any reacts required to pin message


@client.event  # event decorator/wrapper
async def on_ready():
    logger.info(f"Logged in as {client.user}")

    for emoji_id in custom_emoji_ids:
        custom_emoji = client.get_emoji(emoji_id)
        if custom_emoji is None:
            logger.warning(f"Failed to retrieve custom emoji id {emoji_id}")
        else:
            trigger_emojis.add(custom_emoji)


@client.event
async def on_reaction_add(reaction, user):

    message_id = str(reaction.message.id)

    trigger_react_count = sum(react.count for react in reaction.message.reactions if react.emoji in trigger_emojis)
    total_react_count = sum(react.count for react in reaction.message.reactions)
    logger.debug(f"Found {trigger_react_count} trigger reacts, {total_react_count} total reacts on msg {message_id}")

    hard_pin = trigger_react_count == trigger_react_req and total_react_count == trigger_react_req
    soft_pin = total_react_count == total_react_req

    if hard_pin ^ soft_pin: # ^ is XOR, i.e. this will only trigger if it's either hard or soft but not both, to prevent dupes
        pin_reason = f"got {trigger_react_count} trigger react(s)" if hard_pin and not soft_pin else f"got {total_react_count} total reacts"
        logger.info(f"Pinning msg {message_id} because it {pin_reason}")

        pin_channel = client.get_channel(pin_channel_id) #Change editors channel here

        if pin_channel is None:
            logger.warning(f"Failed to send message. Looked for channel id {pin_channel_id}, but found channel object {pin_channel}.")
            await reaction.message.channel.send(f'Message archiving failed at {reaction.message.created_at}. Please '
                                           f'add the id for your review channel to the text file with this code.')
            return

        await pin_channel.send(f'๐ Pinned post from {reaction.message.author.mention} '
                                 f'in <#{reaction.message.channel.id}> '
                                 f'because it {pin_reason}! ๐\n\n'
                                 f'{reaction.message.content}\n\n'
                                 f'Jump to message: {reaction.message.jump_url}\n\n'
                                 f'------------------------------------------------')

        # ## I'm guessing these were used for structured data capture
        # ## Leaving them in for now even though they're not used, might be handy later

        # message_text = reaction.message.content
        # link_index = message_text.find('https://' or 'http://' or 'www.')
        # link = ""
        # if link_index != -1:
        #     link_end_index = message_text.find(' ', link_index)
        #     link = message_text[link_index:(link_end_index if link_end_index != -1 else None)]

        # category = str(reaction.message.channel.category.name)
        # author_id = str(reaction.message.author.id)
        # author_name = str(reaction.message.author.name)
        # pinner_name = str(user.name)
        # pinner_id = str(user.id)
        # pin_channel = str(reaction.message.channel.name)
        # message_url = reaction.message.jump_url

if __name__ == "__main__":
    logger.info(f"Starting up {__name__}")
    client.run(token)
