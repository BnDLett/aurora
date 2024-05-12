# Aurora Bot Alpha

## What is the bot about?
Aurora Bot is a general-purpose Discord bot that is capable of handling more tasks than your typical GP bot can.

## What is it capable of?
It can:
- Get media from a website (YouTube, Soundcloud, etc.)
- Get a post from a Subreddit
- Get information about a Redditor
## Wow, that's not a lot.
Yes! It isn't a lot - for the sole fact that this bot is still in alpha. Certain commands are not yet fully featured 
either. 
## How can I use the code?
1. Clone the repository
2. Install yt_dlp, asyncpraw, and discord-py-interactions via pip. (This will be streamlined in the future)
3. Set up your conf.json file in the below format (order does not matter):
```json
{
  "token": "[your token, string]",
  "debug_token": "[your debug token, string] (optional, necessary if debug is true)",
  "debug_scope": "[the debug scope (test server), string] (optional, necessary if debug is true.",
  "debug": false,  // Remove this comment if copy and pasting. Set this to true if you're debugging code. Bool.
  "reddit_client_id": "[The client ID for Reddit, string] (optional with modification)",
  "reddit_client_secret": "[The secret for the Reddit bot, string] (optional with modification)",
  "reddit_client_agent": "[The client agent for the Reddit bot, string] (optional with modification)"
}
```
4. Remove the comment on the `debug` line. JSON does **not** support comments. 
5. Run the bot.
## How do I disable [this] feature?
Unfortunately, you'll be on your own regarding this documentation. Although, feel free to DM me on Discord (username 
is `bndlett`) and I will try my best to help. 
## How do I request a feature/command?
Open an issue in this GitHub repository or make a suggestion in the Discord server. Please do provide as much 
information about the request as possible.