# FangBot
### Configuration
1. Remove the .sample extensions from the following files:
- .env.sample
- roles.csv.sample
2. Replace the placeholder values in .env with your bot's token, the various IDs for objects, and the limit on pings/emoji in a single post. To grab IDs: enable developer mode in Discord advanced settings, right click on the relevant object, and select "Copy objectname ID".
3. Populate the roles.csv file with the roles you want the bot to grant whenever a user reacts to the welcome post. Syntax should be: emojiname,role ID.