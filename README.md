# FWB Pins 📌
##### Curation by Committee

## Getting Started
1. Create a new Application in the [Discord developers portal](https://discord.com/developers/applications)

2. Clone this repo to your local environment
3. Run ```pip install Discord```
4. Make a copy & rename the `.env.example` file: `cp .env.example .env`
5. Paste your Discord bot token into the appropriate field of `.env` — you'll get this from the developers portal. 
6. Create a channel in your Discord server for the bot to post pinned messages. Paste the channel ID into the appropriate field of `.env`. (Hint: you can check the channel ID easily by typing `\#name-of-channel` in the server).
7. Choose a custom emoji you will use to Pin things in your discord. Paste the emoji ID into the appropriate field of `.env`. (Hint: you can check the emoji ID easily by typing `\:name-of-the-emoji-you-want:` in the server).
8. Invite the bot to your server and give it permission to access all the channels you're pinning from, as well as the review channel where pinned messages will be posted.
9. Run ```python3 fwb_pins.py``` to start the bot!
    - Or, if you're planning on deploying to Heroku, and have the heroku CLI installed & the repo set up to point to a heroku app, you can use the `heroku local` command.


## Functionality
Once running, you will be able to pin messages with both the custom emoji you setup, as well as the native 📌 emoji. The messages you pin will be reposted with their information in the review channel. Additionally, any messages with 15+ reactions, will be pinned automatically. This number can be changed in the ```fwb_pins.py``` file. 

The bot will not recognize any reacts on messages sent before it was started/restarted. 

You will likely want to host this on Heroku so it's always on. 

## Deployment
This repo is ready to be deployed to Heroku.

In broad steps:
1. Fork this repo - you need to own a repo to connect it to Heroku.
2. [Create a Heroku app](https://devcenter.heroku.com/start).
3. Set up [the GitHub deploy method](https://devcenter.heroku.com/articles/github-integration#enabling-github-integration), linking your new app to your fork of this repo.
4. [Create and set the `DISCORD_BOT_TOKEN`, `DISCORD_PIN_CHANNEL_ID`, and `DISCORD_CUSTOM_EMOJI_IDS` environment variables for your Heroku app](https://devcenter.heroku.com/articles/config-vars#managing-config-vars) just like you did for the `.env.example` file above. 
5. [Deploy the app](https://devcenter.heroku.com/articles/github-integration#manual-deploys).
    1. Remember, you might need to activate your worker dyno before anything happens: check the "Resources" tab of your Heroku app, or `heroku ps:scale worker=1` in the cli.
6. You should be live.
