"""
PinBot - Community Curation within the FWB Discord.
As users drop the 📌 emoji on valuable posts, the posts are archived in a database with rich discord data.
These posts are also fed into an 'editors channel' in FWB where our gang of editors can review.
"""
import discord
from discord.utils import get
from discord.ext import commands


# Loads Discord Token from file in parent folder
with open("key.txt", "r") as file:
    token = file.read().replace('\n', '')

with open("review_channel_id.txt", "r") as file:
    log_channel = int(file.read().replace('\n', ''))

with open("custom_emoji_id.txt", "r") as file:
    custom_emoji_id = int(file.read().replace('\n', ''))

client = commands.Bot(command_prefix = "!")
pin_req = 1     #mimimum number of 📌 reactions required to pin message.


@client.event  # event decorator/wrapper
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_reaction_add(reaction, user):

    channel = reaction.message.channel 
    emoji_react = "📌"
    custom_emoji = client.get_emoji(custom_emoji_id)  # Your custom Emoji
    emojicount = 0

    message_id = str(reaction.message.id)

    # Get total reactions for a message and if over 15 treat it the same as a pin
    total_reacts = reaction.message.reactions
    total_count = 0
    for react in total_reacts:
        total_count += react.count

    # Starts code for pinned messages and sets up total emoji for autopinning
    if reaction.emoji == emoji_react or reaction.emoji == custom_emoji or total_count == 15: #Change this number to change the amount of reacts a post needs to get 'pinned'

        if reaction.emoji == custom_emoji or reaction.emoji == emoji_react:
            hard_pin = True
        else:
            hard_pin = False
        

        try:
            # Counts how many times pin emoji was used. This prevents duplicates.
            pin_react = get(reaction.message.reactions, emoji=emoji_react)
            custom_pin = get(reaction.message.reactions, emoji=custom_emoji)
            try:
                custom_pin = custom_pin.count
            except:
                emojicount = pin_react.count

            if emojicount > pin_req or custom_pin > pin_req:
                print("Stopped from pinning twice")
                print(emojicount)
                return

        except Exception as ex:
            print("Pure Emoji Pin")


        message_text = reaction.message.content
        editor_channel = client.get_channel(839991951344009237) #Change editors channel here

        if editor_channel is None:
            await reaction.message.channel.send(f'Message archiving failed at {reaction.message.created_at}. Please '
                                           f'add the id for your review channel to the text file with this code.')
            return

        link_index = message_text.find('https://' or 'http://' or 'www.')

        link = ""
        if link_index != -1:
            link_end_index = message_text.find(' ', link_index)
            link = message_text[link_index:(link_end_index if link_end_index != -1 else None)]

        category = str(reaction.message.channel.category.name)
        message_id = str(reaction.message.id)
        author_id = str(reaction.message.author.id)
        author_name = str(reaction.message.author.name)
        pinner_name = str(user.name)
        pinner_id = str(user.id)
        pin_channel = str(reaction.message.channel.name)
        message_url = reaction.message.jump_url


        await editor_channel.send(f'📌 Pinned post from {reaction.message.author.mention} '
                                 f'in <#{reaction.message.channel.id}>: 📌\n\n'
                                 f'{reaction.message.content}\n\n'
                                 f'Jump to message: {message_url}\n\n'
                                 f'------------------------------------------------')

        # Get total emojis of all type:
        total_reacts = reaction.message.reactions
        total_count = 0
        for react in total_reacts:
            total_count += react.count
        print('Total Reacts: ' + str(total_count))


client.run(token)