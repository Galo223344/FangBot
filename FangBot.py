#This program is free software and licensed under the GNU Affero General Public License verson 3 (AGPL)
#The AGPL can be found in the LICENSE file within this repository
#Alternatively, the AGPL can be found here: https://www.gnu.org/licenses/agpl-3.0.en.html

import os
import random as r
import discord as d
from dotenv import load_dotenv
from discord.ext import commands as dc

load_dotenv()
dtoken = os.getenv('TOKEN')
ints = d.Intents().all()
dBot = dc.Bot(command_prefix='!', intents=ints)

@dBot.event
async def on_ready():
    print(f'{dBot.user.name} has connected to Discord.')

dBot.run(dToken)
