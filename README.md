# FWB Pins

- Create a new Application in the [Discord developers portal](https://discord.com/developers/applications)
- Clone this repo to your local environment.
- Run ```pip install Discord```
- Create a channel in your Discord server for the bot to post pinned messages. Paste the channel ID into ```review_channel.txt```
- Choose a custom emoji you will use to Pin things in your discord. Paste the emoji ID into ```custom_emoji_id.txt```
- Paste your Discord bot token into ```key.txt``` - You'll get this from the developers portal. 
- Invite the bot to your server and give it permission to access all the channels you're pinning from, as well as the review channel where pinned messages will be posted.
- Run ```Python3 fwb_pins.py``` to start the bot

Once running, you will be able to pin messages with both the custom emoji you setup, as well as the native 📌 emoji. The messages you pin will be reposted with their information in the review channel. Additionally, any messages with 15+ reactions, will be pinned automatically. This number can be changed in the ```fwb_pins.py``` file. 
