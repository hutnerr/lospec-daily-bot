## Overview
This Discord bot automatically posts the daily prompt and palette from [Lospec Daily](https://lospec.com/dailies/) to a server, making it easy for consistent pixel art practice.

This is a personal project and has no official affiliation with Lospec.  
The project is licensed under the MIT License.

## Links
- [More Information](https://www.hunter-baker.com/pages/projects/lospec-bot.html)
- [Invite Link](https://discord.com/oauth2/authorize?client_id=1457439367500009597&permissions=2147485696&integration_type=0&scope=bot)

## Commands
> To activate the bot, use `/setchannel` in the channel you want the bot to post to.

- `/getdailydata` - Posts the current Lospec Daily challenge.
- `/toggle` - Enables or disables automatic daily postings.
- `/setchannel` - Sets the channel where daily challenges are posted.
- `/serverconfig` - Displays the current server configuration.
- `/about` - Displays information about the bot.
- `/help` - Displays the command list and usage information.

## Setup
To set this up locally, you would need to provide your own Discord key. You would have to have a `key.json` file within the data folder in root. You also would need to `pip install -r requirements.txt` which is also located in root.

```json
{
  "key": "DISCORD_API_KEY_GOES_HERE",
}
```

## Showcase
<img width="570" height="431" alt="Example of Lospec Daily posted in Discord" src="https://github.com/user-attachments/assets/35636abb-bc5e-4a22-a790-ed0032373dbc"/>

## Support
If you found this project helpful or enjoyable, and want to support future work, you can buy me a coffee on Ko-fi
<br>
Totally optional, always appreciated.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/S6S71TM9XT)
