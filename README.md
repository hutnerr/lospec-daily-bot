> This project is completed and likely will not receive any new features, only maintenance updates.

## Overview
A Discord bot that automatically posts the daily prompt and palette from [Lospec Daily](https://lospec.com/dailies/) to a server, making consistent pixel art practice easy.

**Links:**
- [Invite Link](https://discord.com/oauth2/authorize?client_id=1457439367500009597&permissions=2147485696&integration_type=0&scope=bot)

> View more about the project on its [showcase page](https://www.hunter-baker.com/pages/projects/lospec-bot.html).

## Usage
> To activate the bot, use `/setchannel` in the channel you want the bot to post to.

- `/getdailydata` - Posts the current Lospec Daily challenge.
- `/toggle` - Enables or disables automatic daily postings.
- `/setchannel` - Sets the channel where daily challenges are posted.
- `/serverconfig` - Displays the current server configuration.
- `/about` - Displays information about the bot.
- `/help` - Displays the command list and usage information.

## Setup
To run this locally, you need your own Discord key. The bot reads it from an environment variable, which you can set in a `.env` file in the root of the project.

```bash
pip install -r requirements.txt
```

```env
LOSPEC_BOT_KEY=...
```

## Showcase
<img src="https://github.com/user-attachments/assets/35636abb-bc5e-4a22-a790-ed0032373dbc" alt="Example of Lospec Daily posted in Discord">

## License & Credits
The project is licensed under the MIT License.

This is a personal project and has no official affiliation with Lospec.

## Support
If you found this project helpful or enjoyable, and want to support future work, you can buy me a coffee on Ko-fi
<br><br>
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/S6S71TM9XT)
