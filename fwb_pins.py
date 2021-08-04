"""
FWB Pins - Community Curation ~ Airtable Functionality Removed ~
As users drop the 📌 emoji on valuable posts, the posts are archived in a review channel.

Written by Dexter Tortoriello // @houses for Friends With Benefits
"""

import logging
import os
from collections import defaultdict
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
## á la https://devcenter.heroku.com/articles/heroku-local#set-up-your-local-environment-variables
## For deployment, you'll need to add the env vars to your Heroku app,
## á la https://devcenter.heroku.com/articles/config-vars#managing-config-vars

## The Discord bot token, from the Discord application Bot page
token = os.getenv("DISCORD_BOT_TOKEN")

## Only until the bot commands work
pin_channel_id = int(os.getenv("DISCORD_PIN_CHANNEL_ID"))
custom_emoji_ids = [int(s) for s in os.getenv("DISCORD_CUSTOM_EMOJI_IDS").split(",")]

## Set up the emoji we're using as triggers
pin_emoji = "📌" # That's U+1F4CC if you need to know

"""
Planning: bot-command setting of which pins go where

Flow:
- Parse instructions of which pins go to which channel.
    - !pin :emoji: <channel> "registers" any messages with :emoji: reacts to be pinned to <channel>
    - <channel> should default to the chan where the command was issued.
- Store which pins go to which channel.
    - No reason why a specific emoji can't pipe stuff to >1 channel, so we'll have {emoji_id: {set,of,chan_ids}}.
    - A global dict is fine to start. I don't think we need a db or anything here. Persistence schmersistence.
- On react, check if the emoji is in the dict's keys.
- If it is, pin it to the channels specified for that emoji.

- Would need to support custom emoji as well as unicode emoji — not sure how hard that is.
- Would be useful to have a command to show the current global dict. 
- Would be ideal to limit these commands to specific user roles.

- Do we keep the "hot"/soft-pin 15+ feature?
    - Seems possible, but how do you determine output channel? 
    - Another bot command: !pin hot <15>?
    - If we're doing that, do we keep the "count" requirement, and just default it to 1? So the dict could be
    - {emoji: {(chan_id_1, trigger_emoji_threshold), (chan_id_2, trigger_emoji_threshold)}}…
    - Maybe this means you'd be better off using the chan_ids as keys and their triggers+thresholds as vals? Nah because we want to look up based on the emoji not the channel, and we don't really care about having different thresholds per emoji (e.g. 2 pins or 5 smileys or whatever).
    - So we either handle the "hot" feature as a unique case, or ditch it. 
    - I'd rather ditch it as it's not really useful for looseunit.
    - Ergo: NO, we ditch the "hot" feature.
- Let's remove the "count" requirement, and enforce that 1 of a given emoji is sufficient to be pinned.
- How do we prevent dupes in this world? 
    - More complex, because you want to prevent double-pinning to the _same_ channel, while allowing pinning to multiple channels.
    - i.e. add the :pushpin: to push to one channel, then later add the :some_other_react: to push to a different channel, but not re-push to the first chan.
    - This feels annoying.

- Scenarios:
    - 1 emoji posting to 1 chan
    - 1 emoji posting to 2 different chans
    - 2 different emoji posting to the same chan
    - 2 different emoji posting to 2 independent chans
"""
which_pins_go_where = defaultdict(set)

which_pins_go_where[pin_emoji].add(pin_channel_id)


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
            which_pins_go_where[custom_emoji].add(pin_channel_id)
    logger.debug(f"Pin->Channel dict looks like: {which_pins_go_where}")

@client.event
async def on_reaction_add(reaction, user):

    message_id = str(reaction.message.id)

    trigger_react_count = sum(react.count for react in reaction.message.reactions if react.emoji in which_pins_go_where)
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

        await pin_channel.send(f'📌 Pinned post from {reaction.message.author.mention} '
                                 f'in <#{reaction.message.channel.id}> '
                                 f'because it {pin_reason}! 📌\n\n'
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
