import asyncio
import datetime
import os
import re
import time
import webbrowser
import discord
import json
import requests
import rpg
import math
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

LastDMTimes = {}

ExludedIDs = {472714545723342848, 159985870458322944}  # Banned users: EarTensifier, MEE6


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

    asyncio.create_task(rpg.gameServerLoop())  # This runs the loop for mob spawning etc. No need to await this we leave it

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
    files = []
    for att in attachements:
        f = await att.to_file()
        files.append(f)
    print(f'({servername}) {author.display_name}: {content}')

    # Handling rpg inputs  # Old way to handle the inputs
    # for plr in playerList:
    #     if author.id == plr.ID and len(content) <= 6 and re.match('^[awsd]+$', content):
    #         await rpgInput(content, plr)
    #     if author.id == plr.ID and re.match('^[awsd]+$', content):
    #         await message.delete()
    #     break
    #

    # Dumb stuff:
    if author == Brix:
        await message.delete()
        await channel.send(content, files=files, reference=repliedto)

    if content == "what's updog?":
        await channel.send("Nothing, what's up with you?")

    if ("hello" in message.content.lower().split(' ') or
    "hi" in message.content.lower().split(' ') or
    "hey" in message.content.lower().split(' ') or
    "wsg" in message.content.lower().split(' ')) and not DM:
        try:
            await author.timeout(datetime.timedelta(hours=1), reason="They tried to greet other server members, we do not like that >:(")
            print(f'({servername}) Timeouted {author.display_name} for greeting people')
        except Exception as error:
            if str(error) == "403 Forbidden (error code: 50013): Missing Permissions":
                print(f'({servername}) Could not ban {author.display_name}: No permission')
            else:
                print(f'({servername}) Could not ban {author.display_name}: {error}')

    if "kfestobot" in message.content.lower().split(' ') or client.user.mention in message.content:
        await channel.send("Hello :D", reference=message)


@client.event  # Basically a spying software xd
async def on_message_edit(messageA: discord.Message, messageB: discord.Message):
    if messageA.author.id in ExludedIDs:
        return
    author = messageA.author
    if author == client.user:
        return
    servername = messageA.guild.name
    contentA = messageA.content
    contentB = messageB.content
    channel = messageA.channel

    if contentA == contentB:
        return

    print(f'({servername}) {author.display_name} edited: {contentA} to: {contentB}')
    await channel.send(f'{author.mention} edited: `{contentA}` to: `{contentB}`')


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
        await interaction.response.defer()
        print('xd')
        resetAFKTimeout(self.player)

    @discord.ui.button(label='Menu', style=discord.ButtonStyle.green, row=0)  # please use the menu windows naming scheme from rpg.py player class
    async def ButtonESC(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = await self.player.interaction.original_response()
        await interaction.response.defer()
        if not self.player.screen[:4] == "menu":
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
        msg = await self.player.interaction.original_response()
        await interaction.response.defer()
        if not self.player.screen == "map":
            self.player.screen = "map"
            await updateRender(self.player)
        else:
            self.player.screen = "main"
            await updateRender(self.player)
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


async def refreshRenderLoop(player: rpg.Player):  # SHOULD NOT BE CALLED ANYWHERE BESIDES THE JOIN FUNCTION
    while abs((datetime.datetime.now() - player.afkTimer).seconds) < 300:
        if not player.awaitingDeletion:
            await updateRender(player)
            await asyncio.sleep(1)
        else:
            break

    if not player.awaitingDeletion:
        print(f"(RPG) Killed {player.interaction.user.display_name} for afk")
        await disconnectPlayer(player)

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
    # Call when you want to disconnect player, handles everything for you
    # MAKE SURE TO NOT CALL THIS AS A RESULT OF THE Player.awaitingDeletion TAG TO PREVENT LOOPS
    rpg.dataMatrix[player.position[0]][player.position[1]]["Entity"] = None
    try:
        msg = await player.interaction.original_response()
        await msg.delete()
    except:
        print("(RPG) the game message was lost")
    player.awaitingDeletion = True
    playerList.remove(player)


def takeDamage(player: rpg.Player, damage, base=100):
   # if player.stats[armor] < 0:
   #     player.stats[armor] = 0
    damage_reduction = (player.stats[armor] + 1) / ((player.stats[armor] + 1) + base)
    player.health -= damage*(1 - damage_reduction)
def checkPlayerStatus(player: rpg.Player):
    if player.statusEffects[poison][0] > 0:
        player.health -= player.statusEffects[poison][1]
        player.statusEffects[poison][0] -= 1
    if player.statusEffects[bleed][0] > 0:
        player.health *= player.statusEffects[bleed][1]/100
        player.statusEffects[bleed][0] -= 1
    if player.stats.health <= 0:
        player.alive = False
def combatInitiated(player: rpg.Player,hostileEntity):
    pTurn = True #checks if it's player's turn


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
            await disconnectPlayer(pl)
            was = True
            await interaction.response.send_message("Disconnected from the game!", ephemeral=True)
            print(f"(RPG) {interaction.user.display_name} left the game")
    if not was:
        await interaction.response.send_message("You are not connected to the game!", ephemeral=True)
#

client.run(os.environ["DISCORD_API_KEY"])
# Run the bot, make sure this is always at the end of the file,
# add your API key to the system environment variables under the DISCORD_API_KEY variable,
# DO NOT put your API key in here as a string or I will literally make your bot delete the servers it's in :)
