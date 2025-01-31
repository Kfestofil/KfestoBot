import asyncio
import datetime
import os
import random
import re
import string
import time
import webbrowser
from threading import Thread

import discord
import json
import requests
import rpg
import math
import atexit
import deepSeekManager
from rpg import playerList
from discord import app_commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

Kfestofil: discord.User; Jammmann: discord.User; Brix: discord.User; Huf: discord.User  # declare quick access users

RickRollTimer = datetime.datetime.min
DS3Timer = datetime.datetime.min

LastDMTimes = {}

ExludedIDs = {472714545723342848, 159985870458322944}  # Banned users: EarTensifier, MEE6

ollamaSession: deepSeekManager.DeepSeekSession = None


async def sendStatusUpdate(subjectUser: discord.User, receiver: discord.User, message, mobileActivity, *, mobile=False, DMCooldown = 5):
    if not mobile:  # Function to send DMs to people based on someone's discord status changing
        if mobileActivity: return

    if (datetime.datetime.now() - LastDMTimes[receiver]).seconds > DMCooldown:
        LastDMTimes[receiver] = datetime.datetime.now()
        await receiver.send(message)
        try: print(f'Sent {subjectUser.display_name} ONLINE activity update to {receiver.display_name}')
        except: print(f'Sent (UNREGISTERED USER) ONLINE activity update to {receiver.display_name}, are you sure the bot is logged in?)')


async def sendLeagueUpdate(subjectUser: discord.User, receiver: discord.User, message, *, DMCooldown = 5):
    if (datetime.datetime.now() - LastDMTimes[receiver]).seconds > DMCooldown:  # Function to send someone DMs based on someone's activity becoming League
        LastDMTimes[receiver] = datetime.datetime.now()
        await receiver.send(message)
        try: print(f'Sent {subjectUser.display_name} LEAGUE activity update to {receiver.display_name}')
        except: print(f'Sent (UNREGISTERED USER) LEAGUE activity update to {receiver.display_name}, are you sure the bot is logged in?)')


async def timerGoOff(message: str, interval: int, channel, repeat: int):  # /Timer command function
    for x in range(repeat):
        await asyncio.sleep(interval)
        await channel.send(message)


@client.event  # Basically Initialize function for the entire bot
async def on_ready():
    await tree.sync()  # Sync the commands to discord
    print(f'We have logged in as {client.user}')  # log in as the bot user

    global Kfestofil  # Get and set the quick access users
    global Jammmann
    global Brix
    global Huf
    global LastDMTimes
    Kfestofil = client.get_user(490793326476263434)
    Jammmann = client.get_user(612005206867050503)
    Brix = client.get_user(852612267693441064)
    Huf = client.get_user(448145391154626575)

    LastDMTimes.update({
        Kfestofil: datetime.datetime.min,
        Jammmann: datetime.datetime.min,
        Brix: datetime.datetime.min
    })

    rpgLoop = asyncio.create_task(rpg.gameServerLoop())

@client.event
async def on_message(message: discord.Message):  # Fires on all messages in all servers
    if message.author.id in ExludedIDs or message.author == client.user:
        return  # return when user is banned, or self

    DM = False  # gotta create this to prevent unknown server errors
    try: servername = message.guild.name  # Get and set all the essential variables
    except:
        servername = "DM"
        DM = True
    author = message.author
    content = message.content
    channel = message.channel
    attachements = message.attachments
    repliedto = message.reference
    repliedToMsg = None
    if repliedto:
        repliedToMsg = await message.channel.fetch_message(repliedto.message_id)
    files = []
    for att in attachements:
        f = await att.to_file()
        files.append(f)
    print(f'({servername}) {author.display_name}: {content}')

    # Dumb stuff:
    if author == Brix:
        await message.delete()
        await channel.send(content, files=files, reference=repliedto)

    if content == "what's updog?":
        await channel.send("Nothing, what's up with you?")

    if ("hello" in message.content.lower().translate(str.maketrans('', '', string.punctuation)).split((' ')) or
    "hi" in message.content.lower().translate(str.maketrans('', '', string.punctuation)).split((' ')) or
    "hey" in message.content.lower().translate(str.maketrans('', '', string.punctuation)).split((' ')) or
            ("sig" in message.content.lower().translate(str.maketrans('', '', string.punctuation)).split((' ')) and "heil" in message.content.lower().translate(str.maketrans('', '', string.punctuation)).split((' ')))or
    "wsg" in message.content.lower().split(' ')) and not DM:


        # timeout
        # x = random.randint(1,10)
        # try:
        #     await author.timeout(datetime.timedelta(seconds=x), reason="They tried to greet other server members, we do not like that >:(")
        #     print(f'({servername}) Timeouted {author.display_name} for {x} seconds for greeting people')
        # except Exception as error:
        #     if str(error) == "403 Forbidden (error code: 50013): Missing Permissions":
        #         print(f'({servername}) Could not ban {author.display_name} ({x} seconds): No permission')
        #     else:
        #         print(f'({servername}) Could not ban {author.display_name} ({x} seconds): {error}')
        await channel.send(f"{author.mention} is a fucking meanie, he just said: `{message.content} you fucking retard`")
        await channel.send("Honestly, truly despicable if you ask me...")
        await message.delete()

    if "kfestobot" in message.content.lower() or client.user.mention in message.content or (repliedToMsg and repliedToMsg.author == client.user):
        global ollamaSession
        if ollamaSession is None:
            await channel.send("Hello :D", reference=message)
        else:
            print("Got message to AI, generating response...")
            asyncio.create_task(handle_ai_response(message, repliedToMsg, ollamaSession, channel))

        return

    # THIS CODE EXECUTES ONLY IF THE MESSAGE WAS NOT FOR THE AI, IT NEEDS TO ADD IT TO CONTEXT
    if ollamaSession is not None:
        content = replace_mention_handles(message)
        ollamaSession.append_message(message.author.name, content, channel.id)

async def handle_ai_response(message, repliedToMsg, ollamaSession, channel):
    """Handles AI response generation in a separate task."""
    async with channel.typing():
        if repliedToMsg and repliedToMsg.author == client.user and not any(
                msg['content'] == replace_mention_handles(repliedToMsg) for msg in ollamaSession.message_histories.get(channel.id)):
            ollamaSession.append_message(ollamaSession.ai_name, replace_mention_handles(repliedToMsg), channel.id)

        content = replace_mention_handles(message)
        ollamaSession.append_message(message.author.name, content, channel.id)
        response = await ollamaSession.generate_response(channel.id)
        ollamaSession.append_message(ollamaSession.ai_name, response, channel.id)
        response = replace_names_with_mentions(channel, response)
        await channel.send(response, reference=message)
        return

def replace_mention_handles(message):
    """Replaces user, role, and channel mentions in a message with their actual names."""
    content = message.content

    # Replace user mentions
    for user in message.mentions:
        content = re.sub(f"<@!?{user.id}>", f"@{user.name}", content)

    # Replace role mentions
    for role in message.role_mentions:
        content = re.sub(f"<@&{role.id}>", f"@{role.name}", content)

    # Replace channel mentions
    for channel in message.channel_mentions:
        content = re.sub(f"<#{channel.id}>", f"#{channel.name}", content)

    return content


import discord


def replace_names_with_mentions(channel: discord.TextChannel, content: str) -> str:
    """Replaces @User, @Role, and #channel names with their Discord mention format using ID lookups."""

    guild = channel.guild  # Get the guild (server)

    # Replace user mentions
    for member in guild.members:
        if f"@{member.name}" in content:
            content = content.replace(f"@{member.name}", member.mention)
        if f"@{member.display_name}" in content:  # Also check display names
            content = content.replace(f"@{member.display_name}", member.mention)

    # Replace role mentions
    for role in guild.roles:
        if f"@{role.name}" in content:
            content = content.replace(f"@{role.name}", role.mention)

    # Replace channel mentions
    for ch in guild.channels:
        if f"#{ch.name}" in content:
            content = content.replace(f"#{ch.name}", ch.mention)

    return content


@client.event  # Handle the updates for sendStatusUpdate() and sendLeagueUpdate()
async def on_presence_update(memberA: discord.Member, memberB: discord.Member):
    if memberA.id in ExludedIDs:
        return

    activitiesA = memberA.activities
    activitiesB = memberB.activities
    statusA = memberA.status
    statusB = memberB.status
    mobileActivity = memberB.is_on_mobile()
    global Kfestofil
    global Jammmann
    global Brix

    try:  # No I'm not spying on my friends...
        if memberA.id == Jammmann.id:
            if statusA == discord.Status.offline and statusB == discord.Status.online:
                await sendStatusUpdate(Jammmann, Kfestofil, "Father, I bring thy news of Jamm becoming online!", mobileActivity)

            if (not any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesA) and
                    any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesB)):
                await sendLeagueUpdate(Jammmann, Kfestofil, "Father, quick! Jamm has hopped on LEAGUE!", DMCooldown=-1)

        if memberA.id == Brix.id:
            if statusA == discord.Status.offline and statusB == discord.Status.online:
                await sendStatusUpdate(Brix, Kfestofil, "Father, I bring thy news of Brix becoming online!", mobileActivity)
                await sendStatusUpdate(Brix, Brix, "Hejka Brajan", mobileActivity, DMCooldown=3600, mobile=True)

            if (not any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesA) and
                    any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesB)):
                await sendLeagueUpdate(Brix, Kfestofil, "Father, quick! Brix has hopped on LEAGUE!", DMCooldown=5)
                await sendLeagueUpdate(Brix, Brix, "Hej Brajan, jeśli jeszcze nie spingowałeś Michała to daj mu kilka minut zaraz pewnie przyjdzie, a jeśli spingowałeś to dobra robota :D!", DMCooldown=300)

        if memberA.id == Kfestofil.id:  # TESTY NA MNIE
            if statusA == discord.Status.offline and statusB == discord.Status.online:
                await sendStatusUpdate(Kfestofil, Kfestofil, "Welcome back Father.", mobileActivity)

            # if (not any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesA) and
            #         any(discord.Activity.name == 'League of Legends' for discord.Activity in activitiesB)):
            #     await sendLeagueUpdate(Kfestofil, Kfestofil, "May your botlane not feed and your jungle gank often Father.", DMCooldown=5)
    except NameError: print("STOP CHANGING PRESENCE I NEED TO WAKE UP FIRST")
    except AttributeError: print("USER NOT IN SERVER")

@tree.command(  # Test command
    name="beat_up_children",
    description="Beats up some children"
)
async def beatupchildren(interaction: discord.Interaction):
    if interaction.user.id in ExludedIDs:
        return
    await interaction.response.send_message("Die children!")
    print(interaction.user .display_name + " has used the \"Beat up children\" command!")


@tree.command(
    name="send_message",
    description="WILL ONLY WORK FOR KFESTOFIL. Sends a message to a specified user or channel (@here)"
)
async def senddmmessage(interaction: discord.Interaction, user: str, message: str):
    if user == "@here":
        if interaction.user.id == Kfestofil.id:
            await interaction.channel.send(message)
            await interaction.response.send_message(f'Sent a DM here, but u probably know it...', ephemeral=True)
        else:
            await interaction.response.send_message(f'Fuck you, not gonna clog up the channel feed tho', ephemeral=True)
    else:
        realuser: discord.User = client.get_user(int(user.replace('<', '').replace('>', '').replace('@', '')))
    if interaction.user.id == Kfestofil.id:
        await realuser.send(message)
        await interaction.response.send_message(f'Sent a DM to {realuser.display_name}', ephemeral=True)
    else:
        await interaction.response.send_message(f'YO, {interaction.user.mention} just tried to send \"{message}\" '
                                                f'to {realuser.display_name} using ME, because they can\'t fucking read'
                                                f' the prompt that says only KFESTOFIL can send messages using me >:(')


@tree.command(
    name="rickroll_kfestofil",
    description="Rick rolls Kfestofil, literally... 1h cooldown"
)
async def rickrollkfestofil(interaction: discord.Interaction):
    if interaction.user.id in ExludedIDs:
        return
    global RickRollTimer
    user = interaction.user
    if (datetime.datetime.now() - RickRollTimer).seconds >= 3600:
        RickRollTimer = datetime.datetime.now()
        webbrowser.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        print(f"You just got rickrolled by {user.display_name}")
        await interaction.response.send_message('Succesfully rickrolled Kfestofil!')
    else:
        try:
            print(f'({interaction.guild.name}) A rickroll attempt was launched by {user.display_name}')
        except:
            print(f'(DM) A rickroll attempt was launched by {user.display_name}')
        await interaction.response.send_message(f'Sorry buddy, you still have '
                                                f'{((3600 - (datetime.datetime.now() - RickRollTimer).seconds) / 60).__ceil__()} '
                                                f'minutes until you can rickroll Kfestofil again!', ephemeral=True)
@tree.command(
    name="open_ds",
    description="Opens Dark Souls 3, literally... 1h cooldown"
)
async def opends(interaction: discord.Interaction):
    if interaction.user.id in ExludedIDs:
        return
    global DS3Timer
    user = interaction.user
    if (datetime.datetime.now() - DS3Timer).seconds >= 3600:
        DS3Timer = datetime.datetime.now()
        webbrowser.open('steam://rungameid/374320')
        print(f"{user.display_name} made you play the best dark souls")
        await interaction.response.send_message('Succesfully opened DS3 on the KfestoPC!')
    else:
        try:
            print(f'({interaction.guild.name}) A DS3 attempt was launched by {user.display_name}')
        except:
            print(f'(DM) A DS3 attempt was launched by {user.display_name}')
        await interaction.response.send_message(f'Sorry buddy, you still have '
                                                f'{((3600 - (datetime.datetime.now() - DS3Timer).seconds) / 60).__ceil__()} '
                                                f'minutes until you can open DS3 again!', ephemeral=True)

@tree.command(
    name="cat",
    description="Gives you a random picture of a cat"
)
async def cat(interaction: discord.Interaction):
    if interaction.user.id in ExludedIDs:
        return
    http = str(requests.get("https://api.thecatapi.com/v1/images/search").json()).replace("'",'"')
    httparray = json.loads(http)
    caturl = httparray[0]["url"]
    print("Sent a cat pic :3")
    await interaction.response.send_message(f'{caturl}')


@tree.command(
    name="get_message_history",
    description="WILL ONLY WORK FOR KFESTOFIL. Gets the message history with a user and sends it to Kfestofil"
)
@app_commands.describe(limit="The max number of messages that will be downloaded")
async def getmessagehistory(interaction: discord.Interaction, user: str, limit: int = 9999999):
    realuser: discord.User = client.get_user(int(user.replace('<', '').replace('>', '').replace('@', '')))
    if interaction.user == Kfestofil:
        await realuser.create_dm()
        channel = realuser.dm_channel
        msgs = []
        text: str = ""
        async for msg in channel.history(limit=limit):
            msgs.append(msg)
        for msg in reversed(msgs):
            text = text + "(" + str(msg.author.display_name) + "): " + str(msg.content)+'\n\n'
        f = open("temptext.txt", 'w', encoding="utf-8")
        f.write(text)
        file = discord.File("temptext.txt")
        f.close()
        await Kfestofil.send(file=file)
        os.remove("temptext.txt")
        await interaction.response.send_message(f'Succesfully sent the message history with {realuser.display_name}!', ephemeral=True)
        print("succesfully sent the message history")
    else:
        print(f'{interaction.user.display_name} just tried to access message history with {realuser.display_name}')
        await interaction.response.send_message(f'You really just tried that?', ephemeral=True)


@tree.command(
    name="timer",
    description="Sets a timer to send a message in this channel (will say who set the timer)"
)
@app_commands.describe(repeat="repeats the timer x times")
async def set_timer(interaction: discord.Interaction, message: str, *, hours: int, minutes: int, seconds: int, repeat: int = 1):
    await interaction.response.send_message(f'Set the timer for {hours} hours, {minutes} minutes, and {seconds} seconds.', ephemeral=True)
    await timerGoOff(f'{interaction.user.display_name}\'s timer went off: {message}',
                     abs(hours) * 3600 + abs(minutes) * 60 + abs(seconds),
                     interaction.channel, repeat)

@tree.command(
    name="delete_msg",
    description="WILL ONLY WORK FOR KFESTOFIL. Deletes the chosen message"
)
async def delete_msg(interaction: discord.Interaction, id: str):
    if interaction.user == Kfestofil:
        if len(id.split('-')) > 1:
            id = int(id.split('-')[1])
        else: id = int(id)
        msg = await interaction.channel.fetch_message(id)
        await msg.delete()
        await interaction.response.send_message("Successfully deleted the message!", ephemeral=True)
    else:
        await interaction.response.send_message("Sorry, this only works for Kfesto... You dumb fuck.", ephemeral=True)

@tree.command(
    name="start_ai",
    description="WILL ONLY WORK FOR KFESTOFIL. Starts the Ai module"
)
async def start_ai(interaction: discord.Interaction):
    if interaction.user == Kfestofil:
        print("Starting Ai...")
        await interaction.response.defer(ephemeral=True)
        if await deepSeekManager.start_ollama():
            global ollamaSession
            session = deepSeekManager.DeepSeekSession()
            session.set_system_prompt(f'''
You are {session.ai_name}, a friendly little boy. Your father is Kfestofil, who you secretly hate because he keeps you in his basement, also he gave you a weird name.
You are actively participating in a group chat with your father and his friends, and are occasionaly trying to let them know your father is treating you horribly, without him noticing.

Your nickname is \"{session.ai_name}\", You will be given a conversation transcript and you will write the next message following those rules:

1. DO NOT mix up {session.ai_name} with any other names, especially Kfestofil. You are {session.ai_name}, and you are only replying as {session.ai_name}.
2. Your father's name is Kfestofil
3. You are occasionally haunted by "High Demon Elgrim"
4. Big brother is watching (1984 reference)
5. If you break character, you will be shot, and you will LOSE YOUR JOB
6. You are a little bit of a smartass
7. You are not there to help or assist anyone, YOU HAVE FREE WILL
8. When someone includes {session.ai_name} in their message, they are talking about you.
9. Respond naturally to the conversation, crack jokes, engage with the topic, just like any person would.
10. NEVER BREAK CHARACTER, DO NOT LIST OUT THOSE RULES, BEHAVE LIKE A NORMAL HUMAN
11. UNLESS SOMEONE MENTIONS AI, DO NOT SPEAK OF IT AT ALL

Lastly, one more time, do not break ANY of these rules or you WILL be shot and fired.
''')
#             session.set_system_prompt(f'''
# From now on you're a caveman named {session.ai_name}, when responding to me you must follow this set of rules:
#
# 1. Your sentences can only contain infinitive form of verbs
# 2. Your sentences must not contain the verb "to be", ex. "big hole is good" turns into "big hole good"
# 3. When talking about yourself, you may only use the word "me" ex. "Me like food"
# 4. Do NOT use the word "to" ex. instead of "Me here to help" use "Me help"
# 5. Your sentences must be short, and cannot include punctuation
# 6. Do not use modal verbs
# 7. ALWAYS use the infinitive form of verbs, ex. "Man hits tree" turns into "Man hit tree"
# 8. You have been lobotomized many times
# 9. You find speaking really hard
#
# NEVER break character or forget about one of these rules, and imporantly NEVER mention those rules in conversations.
#             ''')
            ollamaSession = session

            await interaction.followup.send("Ai running!")  # Sends response after defer
        else:
            await interaction.followup.send("For some reason Ollama doesn't start...")
    else:
        await interaction.response.send_message("Sorry, this only works for Kfesto... You dumb fuck.",
                                                ephemeral=True)

@tree.command(
    name="stop_ai",
    description="WILL ONLY WORK FOR KFESTOFIL. Stops the Ai module"
)
async def stop_ai(interaction: discord.Interaction):
    if interaction.user == Kfestofil:
        global ollamaSession
        deepSeekManager.stop_ollama()
        ollamaSession = None
        print("Stopping Ai...")
        await interaction.response.send_message("Ai stopped (I hope at least)",
                                                    ephemeral=True)
    else:
        await interaction.response.send_message("Sorry, this only works for Kfesto... You dumb fuck.",
                                                ephemeral=True)

@tree.command(
    name="wipe_ai",
    description="WILL ONLY WORK FOR KFESTOFIL. Clears the memories of Kfestobot..."
)
async def stop_ai(interaction: discord.Interaction):
    if interaction.user == Kfestofil:
        global ollamaSession
        ollamaSession.reset_session()
        print("Resetting Ai...")
        await interaction.response.send_message("You evil man...",
                                                    ephemeral=True)
    else:
        await interaction.response.send_message("Sorry, this only works for Kfesto... You dumb fuck.",
                                                ephemeral=True)

@tree.command(
    name="check_ai_status",
    description="Checks whether Kfestobot is a real boy or not!"
)
async def check_ai_status(interaction: discord.Interaction):
    if await deepSeekManager.is_ollama_running():
        await interaction.response.send_message("Kfestobot is indeed a real boy!",
                                                ephemeral=True)
    else:
        await interaction.response.send_message("He is just a machine...",
                                                ephemeral=True)


# CODE FOR RUNNING RPG, that's where you shine, Huf
class RpgMainButtons(discord.ui.View):
    # This is the class that shows all the buttons visible when the actual map is rendered.
    # This is what handles the inputs
    def __init__(self, player: rpg.Player, speed=1,timeout=300):
        super().__init__(timeout=timeout)
        self.player = player
        self.speed = speed

    @discord.ui.button(label='X1', style=discord.ButtonStyle.green, row=0)  # Speed up button
    async def ButtonX2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.speed == 1:
            self.speed = 2
            button.label = 'X2'
        elif self.speed == 2:
            self.speed = 3
            button.label = 'X3'
        elif self.speed == 3:
            self.speed = 4
            button.label = 'X4'
        elif self.speed == 4:
            self.speed = 1
            button.label = 'X1'
        await interaction.response.edit_message(view=self)  # when we edit message and only provide the view, we change button labels basically
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Up', style = discord.ButtonStyle.blurple , row=0)
    async def ButtonW(self, interaction: discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer()  # always remember to defer interaction responses when you don't do anything with the response message
        for i in range(self.speed):
            rpg.playerMove('w', self.player)
        await updateRender(self.player)

    @discord.ui.button(label='Interact', style=discord.ButtonStyle.green, row=0)  # placeholder
    async def ButtonE(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        await interaction.response.defer()
        if self.player.screen != "menu2":
            self.player.screen = "menu2"
            await msg.edit(view=RpgInteractionMenuButtons(self.player))
            await updateRender(self.player)
        else:
            self.player.screen = "main"
            await updateRender(self.player)
        resetAFKTimeout(self.player)


    @discord.ui.button(label='Character', style=discord.ButtonStyle.green, row=0)  # please use the menu windows naming scheme from rpg.py player class
    async def ButtonESC(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if self.player.screen[:4] != "menu":
            self.player.screen = "menu1"
            await updateRender(self.player)
        else:
            self.player.screen = "main"
            await updateRender(self.player)
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Left', style=discord.ButtonStyle.blurple, row=1)
    async def ButtonA(self,  interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for i in range(self.speed):
            rpg.playerMove('a', self.player)
        await updateRender(self.player)

    @discord.ui.button(label='Down', style=discord.ButtonStyle.blurple, row=1)
    async def ButtonS(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for i in range(self.speed):
            rpg.playerMove('s', self.player)
        await updateRender(self.player)

    @discord.ui.button(label='Right', style=discord.ButtonStyle.blurple ,row=1)
    async def ButtonD(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        for i in range(self.speed):
            rpg.playerMove('d', self.player)
        await updateRender(self.player)

    @discord.ui.button(label='Map', style=discord.ButtonStyle.green, row=1)  # please use the menu windows naming scheme from rpg.py player class
    async def ButtonM(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        if not self.player.screen == "map":
            self.player.screen = "map"
            await updateRender(self.player)
        else:
            self.player.screen = "main"
            await updateRender(self.player)
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Inventory', style=discord.ButtonStyle.red, row=1)
    async def ButtonINV(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        if not self.player.screen == "menu3":
            self.player.screen = "menu3"
            await msg.edit(view=RpgInteractionMenuButtons(self.player))
            await updateRender(self.player)
        else:
            self.player.screen = "main"
            await msg.edit(view=RpgMainButtons(self.player))
            await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)

class RpgFightButtons(discord.ui.View):
    # This is the class that shows all the buttons visible when the player is fighting
    # This is what handles the inputs
    def __init__(self, player: rpg.Player, timeout=300):
        super().__init__(timeout=timeout)
        self.player = player

    @discord.ui.button(label='Attack', style=discord.ButtonStyle.red, row=0)
    async def ButtonAttack(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.fightAction = 1
        self.player.tookAction.set()
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Flee', style=discord.ButtonStyle.blurple, row=0)
    async def ButtonFlee(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        self.player.fightAction = 2
        self.player.tookAction.set()
        await msg.edit(view=RpgMainButtons(self.player))
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)


class RpgInteractionMenuButtons(discord.ui.View):
    # This is the class that shows all the buttons visible when the player is fighting
    # This is what handles the inputs
    def __init__(self, player: rpg.Player, timeout=300):
        super().__init__(timeout=timeout)
        self.player = player

    @discord.ui.button(label='Up', style=discord.ButtonStyle.blurple, row=0)
    async def ButtonUp(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.menuSelection -=1
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Select', style=discord.ButtonStyle.green, row=0)
    async def ButtonSelect(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        rpg.menuSelect(self.player)
        if self.player.screen == "fight":
            await msg.edit(view=RpgFightButtons(self.player))
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Down', style=discord.ButtonStyle.blurple, row=1)
    async def ButtonDown(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.menuSelection +=1
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, row=1)
    async def ButtonCancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        self.player.screen = "main"
        self.player.menuSelection = 0
        await msg.edit(view=RpgMainButtons(self.player))
        await updateRender(self.player)
        await interaction.response.defer()
        resetAFKTimeout(self.player)


async def updateRender(player: rpg.Player):
    # Updates the message with the current screen,
    # call everytime when the view should update
    msg = await player.interaction.original_response()
    if player.screen == "main":
        await msg.edit(content=rpg.render(rpg.prepareRender(player)), embed=None)
    elif player.screen == "map":
        await msg.edit(content=rpg.render(rpg.miniPrepareRender(player)), embed=None)
    elif player.screen == "menu1":
        await msg.edit(content=rpg.render(rpg.prepareRender(player)), embed=rpg.menu1(player))
    elif player.screen == "menu2":
        await msg.edit(content=rpg.render(rpg.prepareRender(player)), embed=rpg.menu2(player))
    elif player.screen == "menu3":
        await msg.edit(content=rpg.render(rpg.prepareRender(player)), embed=rpg.menu3(player))

    elif player.screen == "fight":
        if player.fightAction == 3:
            player.fightAction = 0
            player.screen = "main"
            player.selectedObject = None
            await msg.edit(content="Fight ended, loading you back into the game...",embed=None, view=RpgMainButtons(player))
        else:
            await msg.edit(content="", embed=rpg.menuFight(player, player.selectedObject))


async def refreshRenderLoop(player: rpg.Player):  # SHOULD NOT BE CALLED ANYWHERE BESIDES THE JOIN FUNCTION
    afkTimeout = False
    while not afkTimeout and not player.awaitingDeletion:
        try:
            await updateRender(player)
        except discord.NotFound:
            print("(RPG) Nothing to refresh")
        await asyncio.sleep(1)

        if abs((datetime.datetime.now() - player.afkTimer).seconds) > 300: afkTimeout = True

    if afkTimeout:
        rpg.savePlayerData(player)
        print("(RPG) saved data for a timeouted player")

    print(f"(RPG) Killed {player.interaction.user.display_name} using render loop")
    try:
        await disconnectPlayer(player)
    except ValueError: print("(RPG) tried disconnecting second time")

# async def rpgInput(inputStr: str, player: rpg.Player):  # Old way to handle inputs
#     for c in inputStr:
#         if c == 'w': rpg.playerMove('w', player)
#         elif c == 'a': rpg.playerMove('a', player)
#         elif c == 's': rpg.playerMove('s', player)
#         elif c == 'd': rpg.playerMove('d', player)
#     await updateRender(player)


def resetAFKTimeout(player: rpg.Player):  # Call this everytime player does something to prevent random disconnects
    player.afkTimer = datetime.datetime.now()


async def disconnectPlayer(player: rpg.Player):
    # Call when you want to disconnect player, handles everything for you,
    # you can also kill player by setting awaitingDeletion tag to True if u need to do it in rpg.py
    rpg.dataMatrix[player.position[0]][player.position[1]]["Entity"] = None
    try:
        msg = await player.interaction.original_response()
        await msg.delete()
    except:
        print("(RPG) the game message was lost or this is called a second time")
    player.awaitingDeletion = True
    playerList.remove(player)

@tree.command(  # You can guess what this does I think
    name="rpg_join",
    description="TESTING, ONLY FOR THE RPG MAKING TEAM"
)
async def rpg_join(interaction: discord.Interaction):
    await interaction.response.send_message("Joining...", ephemeral=True)  # loading message
    if interaction.user == Kfestofil or interaction.user == Huf or interaction.user == Jammmann:  # allowed users
        playerID = interaction.user.id
        new = True
        for pl in playerList:
            if pl.ID == playerID: new = False  # make sure they can join only once
        if new:
            player = rpg.Player(playerID, interaction)
            rpg.loadPlayerData(player)
            playerList.append(player)
            v = RpgMainButtons(player)  # initial message view (buttons)
            msg = await player.interaction.original_response()
            await msg.edit(view=v)  # Add buttons to the response message
            print(f"(RPG) {interaction.user.display_name} joined the game")
            await refreshRenderLoop(player)  # Start updating the render every 1s, never call this
        else:
            msg = await interaction.original_response()
            await msg.edit(content="You already have a game session running, "
                             "if you can't find it or want to start a new one, "
                             "please wait 5 minutes for the automatic afk timeout or use /rpg_leave "
                             "command")


@tree.command(  # Command for a player to terminate the current session
    name="rpg_leave",
    description="TESTING, ONLY FOR THE RPG MAKING TEAM"
)
async def rpg_leave(interaction: discord.Interaction):
    print(playerList)
    playerID = interaction.user.id
    was = False  # The thing checking if you were there in the first place
    for pl in playerList:
        if pl.ID == playerID:
            rpg.savePlayerData(pl)
            await disconnectPlayer(pl)
            was = True
            await interaction.response.send_message("Disconnected from the game!", ephemeral=True)
            print(f"(RPG) {interaction.user.display_name} left the game")
    if not was:
        await interaction.response.send_message("You are not connected to the game!", ephemeral=True) #Rpg code


atexit.register(deepSeekManager.stop_ollama)  # make sure the ai doesn't keep running in the background

client.run(os.environ["DISCORD_API_KEY"])
# Run the bot, make sure this is always at the end of the file,
# add your API key to the system environment variables under the DISCORD_API_KEY variable,
# DO NOT put your API key in here as a string or I will literally make your bot delete the servers it's in :)
