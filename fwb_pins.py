"""
FWB Pins - Community Curation ~ Airtable Functionality Removed ~
As users drop the 📌 emoji on valuable posts, the posts are archived in a review channel.

Written by Dexter Tortoriello // @houses for Friends With Benefits
"""

import logging
from discord.ext import commands

# logging setup (I hate how much boilerplate this is!)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

client = commands.Bot(command_prefix = "!")

## Discord interaction params
with open("key.txt", "r") as file:
    token = file.read().replace('\n', '')

with open("review_channel_id.txt", "r") as file:
    review_channel_id = int(file.read().replace('\n', ''))

with open("custom_emoji_id.txt", "r") as file:
    custom_emoji_ids = [int(s.strip()) for s in file.read().split('\n')]

## Set up the emoji we're using as triggers
pin_emoji = "📌" # That's U+1F4CC if you need to know
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
    logger.info(f"Found {trigger_react_count} trigger reacts, {total_react_count} total reacts on msg {message_id}")

    hard_pin = trigger_react_count == trigger_react_req and total_react_count == trigger_react_req
    soft_pin = total_react_count == total_react_req

    if hard_pin ^ soft_pin: # ^ is XOR, i.e. this will only trigger if it's either hard or soft but not both, to prevent dupes
        pin_reason = f"got {trigger_react_count} trigger react(s)" if hard_pin and not soft_pin else f"got {total_react_count} total reacts"
        logger.info(f"Pinning msg {message_id} because it {pin_reason}")

        review_channel = client.get_channel(review_channel_id) #Change editors channel here

        if review_channel is None:
            await reaction.message.channel.send(f'Message archiving failed at {reaction.message.created_at}. Please '
                                           f'add the id for your review channel to the text file with this code.')
            return

        await review_channel.send(f'📌 Pinned post from {reaction.message.author.mention} '
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
    client.run(token)
